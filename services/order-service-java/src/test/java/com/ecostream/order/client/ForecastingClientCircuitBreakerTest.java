package com.ecostream.order.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.util.UUID;
import java.util.function.Supplier;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.ExpectedCount.times;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withServerError;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/**
 * Verifies Resilience4j circuit breaker behaviour around the forecast client.
 * Uses a manual CircuitBreakerRegistry (no Spring context needed) to keep the test
 * fast and independent of the database.
 */
class ForecastingClientCircuitBreakerTest {

    private ForecastingClientImpl client;
    private MockRestServiceServer mockServer;
    private CircuitBreakerRegistry registry;

    private static final String BASE_URL = "http://localhost:5050";

    @BeforeEach
    void setUp() {
        RestTemplate restTemplate = new RestTemplate();
        mockServer = MockRestServiceServer.bindTo(restTemplate).build();
        client = new ForecastingClientImpl(BASE_URL, restTemplate, new ObjectMapper());

        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
                .slidingWindowSize(5)
                .failureRateThreshold(50)
                .minimumNumberOfCalls(3)
                .waitDurationInOpenState(Duration.ofSeconds(60))
                .permittedNumberOfCallsInHalfOpenState(1)
                .build();
        registry = CircuitBreakerRegistry.of(config);
    }

    /** Wraps a client call through the circuit breaker, returning null on failure. */
    private ForecastResponseDTO callWithBreaker(CircuitBreaker cb, UUID orderId) {
        Supplier<ForecastResponseDTO> decorated = CircuitBreaker.decorateSupplier(cb,
                () -> client.getForecast(orderId, 49.2276, -123.0076, "Standard"));
        try {
            return decorated.get();
        } catch (Exception e) {
            return null;
        }
    }

    @Test
    void fallbackReturnsNullWhenServiceFails() {
        CircuitBreaker cb = registry.circuitBreaker("forecastService");
        UUID orderId = UUID.randomUUID();

        mockServer.expect(requestTo(BASE_URL + "/api/forecast/" + orderId))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withServerError());

        ForecastResponseDTO result = callWithBreaker(cb, orderId);

        assertNull(result, "Should return null when the AI service errors");
        mockServer.verify();
    }

    @Test
    void circuitOpensAfterRepeatedFailuresAndStopsCallingServer() {
        CircuitBreaker cb = registry.circuitBreaker("forecastService");
        UUID orderId = UUID.randomUUID();
        String url = BASE_URL + "/api/forecast/" + orderId;

        // 3 failures → meets minimumNumberOfCalls, failure rate 100% > 50% → OPEN
        mockServer.expect(times(3), requestTo(url))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withServerError());

        for (int i = 0; i < 3; i++) {
            callWithBreaker(cb, orderId);
        }
        mockServer.verify();

        assertEquals(CircuitBreaker.State.OPEN, cb.getState(),
                "Circuit should be OPEN after 3 consecutive failures");

        // Next call must NOT reach the server — circuit is open
        ForecastResponseDTO result = callWithBreaker(cb, orderId);
        assertNull(result, "Should return null while circuit is OPEN (no server call)");
    }

    @Test
    void successfulCallKeepsCircuitClosed() {
        CircuitBreaker cb = registry.circuitBreaker("forecastService");
        UUID orderId = UUID.randomUUID();

        mockServer.expect(requestTo(BASE_URL + "/api/forecast/" + orderId))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess(
                        "{\"distance_km\": 5.0, \"estimated_arrival_minutes\": 10.0}",
                        MediaType.APPLICATION_JSON));

        ForecastResponseDTO result = callWithBreaker(cb, orderId);

        assertNotNull(result);
        assertEquals(5.0, result.distanceKm());
        assertEquals(10.0, result.estimatedArrivalMinutes());
        assertEquals(CircuitBreaker.State.CLOSED, cb.getState(),
                "Circuit should stay CLOSED after a successful call");
        mockServer.verify();
    }
}
