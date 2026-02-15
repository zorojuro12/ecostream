package com.ecostream.order.client;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Request body for the AI Forecasting Service (Python).
 * Uses snake_case so the JSON matches ForecastRequest in Python.
 */
public record ForecastRequestDTO(
        @JsonProperty("destination_latitude") Double destinationLatitude,
        @JsonProperty("destination_longitude") Double destinationLongitude,
        @JsonProperty("priority") String priority
) {
}
