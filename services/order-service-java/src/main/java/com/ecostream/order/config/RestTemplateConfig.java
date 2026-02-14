package com.ecostream.order.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

/**
 * Provides RestTemplate for outbound HTTP calls (e.g. AI Forecasting Service).
 * Configures 500ms connect and read timeouts for fast failure.
 */
@Configuration
public class RestTemplateConfig {

    private static final Duration TIMEOUT = Duration.ofMillis(500);

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(TIMEOUT)
                .setReadTimeout(TIMEOUT)
                .build();
    }
}
