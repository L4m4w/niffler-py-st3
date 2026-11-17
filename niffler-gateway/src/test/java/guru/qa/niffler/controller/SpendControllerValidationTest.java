package guru.qa.niffler.controller;

import guru.qa.niffler.service.GlobalExceptionHandler;
import guru.qa.niffler.service.SpendClient;
import guru.qa.niffler.service.UserDataClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import org.springframework.core.MethodParameter;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.bind.support.WebDataBinderFactory;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.method.support.ModelAndViewContainer;

import java.util.UUID;
import java.util.stream.Stream;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.http.MediaType.APPLICATION_JSON;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class SpendControllerValidationTest {

  private static final String USERNAME = "test-user";
  private static final String SPEND_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6";

  private SpendClient spendClient;
  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    spendClient = mock(SpendClient.class);
    UserDataClient userDataClient = mock(UserDataClient.class);
    GlobalExceptionHandler exceptionHandler = new GlobalExceptionHandler();
    ReflectionTestUtils.setField(exceptionHandler, "appName", "niffler-gateway");

    Jwt principal = Jwt.withTokenValue("test-token")
        .header("alg", "none")
        .claim("sub", USERNAME)
        .build();

    mockMvc = MockMvcBuilders
        .standaloneSetup(new SpendController(spendClient, userDataClient))
        .setControllerAdvice(exceptionHandler)
        .setCustomArgumentResolvers(new HandlerMethodArgumentResolver() {
          @Override
          public boolean supportsParameter(MethodParameter parameter) {
            return parameter.hasParameterAnnotation(AuthenticationPrincipal.class);
          }

          @Override
          public Object resolveArgument(MethodParameter parameter,
                                        ModelAndViewContainer mavContainer,
                                        NativeWebRequest webRequest,
                                        WebDataBinderFactory binderFactory) {
            return principal;
          }
        })
        .build();

    when(spendClient.addSpend(any())).thenAnswer(invocation -> invocation.getArgument(0));
    when(spendClient.editSpend(any())).thenAnswer(invocation -> invocation.getArgument(0));
  }

  static Stream<String> invalidCategoryNames() {
    return Stream.of("", "   ", "A", "x".repeat(51));
  }

  static Stream<String> validCategoryNames() {
    return Stream.of("AB", "x".repeat(50));
  }

  @ParameterizedTest(name = "POST /api/spends/add rejects category.name of length {0}")
  @MethodSource("invalidCategoryNames")
  void addSpendShouldRejectInvalidCategoryName(String categoryName) throws Exception {
    mockMvc.perform(post("/api/spends/add")
            .contentType(APPLICATION_JSON)
            .content(spendJson(null, categoryName)))
        .andExpect(status().isBadRequest());
    verifyNoInteractions(spendClient);
  }

  @ParameterizedTest(name = "PATCH /api/spends/edit rejects category.name of length {0}")
  @MethodSource("invalidCategoryNames")
  void editSpendShouldRejectInvalidCategoryName(String categoryName) throws Exception {
    mockMvc.perform(patch("/api/spends/edit")
            .contentType(APPLICATION_JSON)
            .content(spendJson(SPEND_ID, categoryName)))
        .andExpect(status().isBadRequest());
    verifyNoInteractions(spendClient);
  }

  @ParameterizedTest(name = "POST /api/spends/add accepts category.name of length {0}")
  @MethodSource("validCategoryNames")
  void addSpendShouldAcceptBoundaryCategoryName(String categoryName) throws Exception {
    mockMvc.perform(post("/api/spends/add")
            .contentType(APPLICATION_JSON)
            .content(spendJson(null, categoryName)))
        .andExpect(status().isCreated());
    verify(spendClient).addSpend(argThat(spend ->
        USERNAME.equals(spend.username()) && USERNAME.equals(spend.category().username())));
  }

  @ParameterizedTest(name = "PATCH /api/spends/edit accepts category.name of length {0}")
  @MethodSource("validCategoryNames")
  void editSpendShouldAcceptBoundaryCategoryName(String categoryName) throws Exception {
    mockMvc.perform(patch("/api/spends/edit")
            .contentType(APPLICATION_JSON)
            .content(spendJson(SPEND_ID, categoryName)))
        .andExpect(status().isOk());
    verify(spendClient).editSpend(argThat(spend ->
        USERNAME.equals(spend.username()) && USERNAME.equals(spend.category().username())));
  }

  @Test
  void addSpendShouldRejectNullCategory() throws Exception {
    mockMvc.perform(post("/api/spends/add")
            .contentType(APPLICATION_JSON)
            .content(spendJson(null, null)))
        .andExpect(status().isBadRequest());
    verifyNoInteractions(spendClient);
  }

  @Test
  void editSpendShouldRejectNullCategory() throws Exception {
    mockMvc.perform(patch("/api/spends/edit")
            .contentType(APPLICATION_JSON)
            .content(spendJson(SPEND_ID, null)))
        .andExpect(status().isBadRequest());
    verifyNoInteractions(spendClient);
  }

  private static String spendJson(String id, String categoryName) {
    return """
        {
          %s
          "spendDate": "2024-06-01T12:00:00.000+00:00",
          "category": %s,
          "currency": "RUB",
          "amount": 10.5,
          "description": "regression test"
        }
        """.formatted(
        id == null ? "" : "\"id\": \"%s\",".formatted(id),
        categoryName == null ? "null" : "{\"name\": \"%s\"}".formatted(categoryName)
    );
  }
}
