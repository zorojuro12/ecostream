package com.ecostream.order.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.test.web.client.match.MockRestRequestMatchers;
import org.springframework.test.web.client.response.MockRestResponseCreators;
import org.springframework.web.client.RestTemplate;

import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Verifies that ForecastingClientImpl sends a non-empty JSON body when calling the AI service.
 * TDD: if the real Python service receives body_captured_len=0, this test proves whether
 * the Java client is actually writing the body (test passes = client sends body; then issue is transport/Python).
 */
class ForecastingClientImplTest {

    private RestTemplate restTemplate;
    private MockRestServiceServer mockServer;
    private final AtomicReference<byte[]> capturedBody = new AtomicReference<>();

    @BeforeEach
    void setUp() {
        restTemplate = new RestTemplate();
        // Capture the exact body bytes that RestTemplate would send (as passed to the execution chain).
        restTemplate.getInterceptors().add((request, body, execution) -> {
            capturedBody.set(body != null ? body : new byte[0]);
            return execution.execute(request, body);
        });
        mockServer = MockRestServiceServer.bindTo(restTemplate).build();
    }

    @Test
    void getForecast_sendsNonEmptyJsonBodyWithSnakeCaseFields() throws Exception {
        UUID orderId = UUID.fromString("11111111-2222-3333-4444-555555555555");
        String baseUrl = "http://localhost:5050";
        String expectedUrl = baseUrl + "/api/forecast/" + orderId;

        mockServer
                .expect(MockRestRequestMatchers.requestTo(expectedUrl))
                .andExpect(MockRestRequestMatchers.method(HttpMethod.POST))
                .andExpect(MockRestRequestMatchers.content().contentType(MediaType.APPLICATION_JSON))
                .andRespond(MockRestResponseCreators.withSuccess(
                        "{\"distance_km\": 12.5, \"estimated_arrival_minutes\": 18.0}",
                        MediaType.APPLICATION_JSON));

        ForecastingClientImpl client = new ForecastingClientImpl(baseUrl, restTemplate, new ObjectMapper());
        client.getForecast(orderId, 37.7749, -122.4194, "Standard");

        mockServer.verify();

        byte[] body = capturedBody.get();
        assertNotNull(body, "Request body must be captured");
        assertTrue(body.length > 0, "Request body must be non-empty (Python was receiving 0 bytes)");
        String bodyStr = new String(body, java.nio.charset.StandardCharsets.UTF_8);
        assertTrue(bodyStr.contains("destination_latitude"), "Body must contain destination_latitude (snake_case for Python)");
        assertTrue(bodyStr.contains("destination_longitude"), "Body must contain destination_longitude");
        assertTrue(bodyStr.contains("priority"), "Body must contain priority");
    }
}
