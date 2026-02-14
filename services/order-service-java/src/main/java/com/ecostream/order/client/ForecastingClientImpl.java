package com.ecostream.order.client;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Map;
import java.util.UUID;

/**
 * RestTemplate-based client for the AI Forecasting Service at http://localhost:5000.
 */
@Component
public class ForecastingClientImpl implements ForecastingClient {

    private static final String BASE_URL = "http://localhost:5000";
    private final RestTemplate restTemplate;

    public ForecastingClientImpl(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Override
    public ForecastResponseDTO getForecast(UUID orderId, Double destinationLatitude,
                                           Double destinationLongitude, String priority) {
        String url = BASE_URL + "/api/forecast/" + orderId;
        Map<String, Object> body = Map.of(
                "destination_latitude", destinationLatitude,
                "destination_longitude", destinationLongitude,
                "priority", priority != null ? priority : "Standard"
        );
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);
        return restTemplate.postForObject(url, request, ForecastResponseDTO.class);
    }
}
