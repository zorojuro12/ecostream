package com.ecostream.order.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object for geographic location coordinates.
 * Used for order destinations and telemetry tracking.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LocationDTO {

    /**
     * Latitude coordinate of the location.
     * Must be between -90 and 90 degrees (inclusive).
     */
    @NotNull(message = "Latitude is required")
    @Min(value = -90, message = "Latitude must be between -90 and 90")
    @Max(value = 90, message = "Latitude must be between -90 and 90")
    private Double latitude;

    /**
     * Longitude coordinate of the location.
     * Must be between -180 and 180 degrees (inclusive).
     */
    @NotNull(message = "Longitude is required")
    @Min(value = -180, message = "Longitude must be between -180 and 180")
    @Max(value = 180, message = "Longitude must be between -180 and 180")
    private Double longitude;
}
