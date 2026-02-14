package com.ecostream.order.client;

import java.util.UUID;

/**
 * Client for the AI Forecasting Service (Python, port 5000).
 * Fetches ETA and distance for an order given its destination and priority.
 */
public interface ForecastingClient {

    /**
     * Calls POST /api/forecast/{orderId} with destination and priority.
     *
     * @param orderId             the order UUID
     * @param destinationLatitude destination latitude
     * @param destinationLongitude destination longitude
     * @param priority            "Express" or "Standard" for ML speed prediction
     * @return forecast with distance_km and estimated_arrival_minutes, or null on failure
     */
    ForecastResponseDTO getForecast(UUID orderId, Double destinationLatitude,
                                   Double destinationLongitude, String priority);
}
