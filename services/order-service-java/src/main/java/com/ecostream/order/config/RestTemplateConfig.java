package com.ecostream.order.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.BufferingClientHttpRequestFactory;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

/**
 * Provides RestTemplate for outbound HTTP calls (e.g. AI Forecasting Service).
 * Configures 500ms connect and read timeouts for fast failure.
 * Uses BufferingClientHttpRequestFactory so the POST body is fully buffered and sent
 * (avoids body being dropped when Python receives Content-Length but 0 bytes).
 */
@Configuration
public class RestTemplateConfig {

    private static final Duration TIMEOUT = Duration.ofMillis(500);

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .requestFactory(() -> new BufferingClientHttpRequestFactory(new SimpleClientHttpRequestFactory()))
                .setConnectTimeout(TIMEOUT)
                .setReadTimeout(TIMEOUT)
                .build();
    }
}
