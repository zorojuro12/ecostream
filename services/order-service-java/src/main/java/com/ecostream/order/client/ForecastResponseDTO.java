package com.ecostream.order.client;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Response DTO from the AI Forecasting Service (Python).
 * Maps snake_case JSON: distance_km, estimated_arrival_minutes.
 */
public record ForecastResponseDTO(
        @JsonProperty("distance_km") Double distanceKm,
        @JsonProperty("estimated_arrival_minutes") Double estimatedArrivalMinutes
) {
}
