package com.ecostream.order.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for telemetry ingestion request body.
 * Uses currentLatitude/currentLongitude to align with client scripts and Telemetry entity.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TelemetryRequestDTO {

    @NotNull(message = "Current latitude is required")
    @Min(value = -90, message = "Latitude must be between -90 and 90")
    @Max(value = 90, message = "Latitude must be between -90 and 90")
    private Double currentLatitude;

    @NotNull(message = "Current longitude is required")
    @Min(value = -180, message = "Longitude must be between -180 and 180")
    @Max(value = 180, message = "Longitude must be between -180 and 180")
    private Double currentLongitude;
}
