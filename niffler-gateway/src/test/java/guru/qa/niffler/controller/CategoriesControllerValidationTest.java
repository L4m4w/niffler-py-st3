package guru.qa.niffler.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import guru.qa.niffler.model.CategoryJson;
import guru.qa.niffler.service.SpendClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.core.MethodParameter;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;
import org.springframework.web.bind.support.WebDataBinderFactory;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.method.support.ModelAndViewContainer;

import java.util.UUID;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.springframework.http.MediaType.APPLICATION_JSON;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ExtendWith(MockitoExtension.class)
class CategoriesControllerValidationTest {

  private static final String USERNAME = "duck";
  private static final UUID CATEGORY_ID = UUID.fromString("06fe9c06-ae67-406e-a711-ba729e3d4775");

  @Mock
  private SpendClient spendClient;

  private MockMvc mockMvc;
  private final ObjectMapper om = new ObjectMapper();

  @BeforeEach
  void setUp() {
    LocalValidatorFactoryBean validator = new LocalValidatorFactoryBean();
    validator.afterPropertiesSet();
    mockMvc = MockMvcBuilders.standaloneSetup(new CategoriesController(spendClient))
        .setValidator(validator)
        .setCustomArgumentResolvers(new TestJwtPrincipalArgumentResolver())
        .build();
  }

  @ParameterizedTest
  @MethodSource("invalidCategoryNames")
  void invalidCategoryNameShouldBeRejected(String name) throws Exception {
    final CategoryJson request = new CategoryJson(CATEGORY_ID, name, USERNAME, false);

    MvcResult mvcResult = mockMvc.perform(patch("/api/categories/update")
            .contentType(APPLICATION_JSON)
            .content(om.writeValueAsString(request)))
        .andReturn();

    assertAll("invalid name must be rejected without downstream update",
        () -> assertEquals(HttpStatus.BAD_REQUEST.value(), mvcResult.getResponse().getStatus()),
        () -> verify(spendClient, never()).updateCategory(any(CategoryJson.class)));
  }

  @ParameterizedTest
  @MethodSource("validBoundaryCategoryNames")
  void boundaryCategoryNameShouldBeAccepted(String name) throws Exception {
    final CategoryJson request = new CategoryJson(CATEGORY_ID, name, USERNAME, true);

    Mockito.when(spendClient.updateCategory(any(CategoryJson.class)))
        .thenAnswer(invocation -> invocation.getArgument(0));

    mockMvc.perform(patch("/api/categories/update")
            .contentType(APPLICATION_JSON)
            .content(om.writeValueAsString(request)))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.id").value(CATEGORY_ID.toString()))
        .andExpect(jsonPath("$.name").value(name))
        .andExpect(jsonPath("$.username").value(USERNAME))
        .andExpect(jsonPath("$.archived").value(true));

    ArgumentCaptor<CategoryJson> captor = ArgumentCaptor.forClass(CategoryJson.class);
    verify(spendClient).updateCategory(captor.capture());
    CategoryJson actual = captor.getValue();
    assertAll("category forwarded downstream",
        () -> assertEquals(CATEGORY_ID, actual.id()),
        () -> assertEquals(name, actual.name()),
        () -> assertEquals(USERNAME, actual.username()),
        () -> assertTrue(actual.archived()));
  }

  private static Stream<String> invalidCategoryNames() {
    return Stream.of("", "   ", "A", "A".repeat(51));
  }

  private static Stream<String> validBoundaryCategoryNames() {
    return Stream.of("AA", "A".repeat(50));
  }

  private static class TestJwtPrincipalArgumentResolver implements HandlerMethodArgumentResolver {

    private final Jwt jwt = Jwt.withTokenValue("test-token")
        .header("alg", "none")
        .claim("sub", USERNAME)
        .build();

    @Override
    public boolean supportsParameter(MethodParameter parameter) {
      return parameter.hasParameterAnnotation(AuthenticationPrincipal.class)
          && Jwt.class.isAssignableFrom(parameter.getParameterType());
    }

    @Override
    public Object resolveArgument(MethodParameter parameter,
                                  ModelAndViewContainer mavContainer,
                                  NativeWebRequest webRequest,
                                  WebDataBinderFactory binderFactory) {
      return jwt;
    }
  }
}
