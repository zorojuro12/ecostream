package com.ecostream.order.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.UUID;

/**
 * RestTemplate-based client for the AI Forecasting Service.
 * Base URL from application.properties (ai.forecasting.base-url); default 5050 (5000-5035 often excluded on Windows).
 * Serializes request body to JSON explicitly so the Python service receives a non-empty body.
 */
@Component
public class ForecastingClientImpl implements ForecastingClient {

    private final String baseUrl;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public ForecastingClientImpl(
            @Value("${ai.forecasting.base-url:http://localhost:5050}") String baseUrl,
            RestTemplate restTemplate,
            ObjectMapper objectMapper) {
        this.baseUrl = baseUrl;
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    @Override
    public ForecastResponseDTO getForecast(UUID orderId, Double destinationLatitude,
                                           Double destinationLongitude, String priority) {
        // No trailing slash: matches FastAPI route POST /api/forecast/{order_id} and avoids 307 redirect (which drops body)
        String url = baseUrl + "/api/forecast/" + orderId.toString();
        ForecastRequestDTO body = new ForecastRequestDTO(
                destinationLatitude,
                destinationLongitude,
                priority != null ? priority : "Standard"
        );
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        String jsonBody;
        try {
            jsonBody = objectMapper.writeValueAsString(body);
        } catch (Exception e) {
            throw new RuntimeException("Failed to serialize forecast request", e);
        }
        HttpEntity<String> entity = new HttpEntity<>(jsonBody, headers);
        ResponseEntity<ForecastResponseDTO> response =
                restTemplate.exchange(url, HttpMethod.POST, entity, ForecastResponseDTO.class);
        return response.getBody();
    }
}
