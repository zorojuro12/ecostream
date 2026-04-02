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
 * Uses BufferingClientHttpRequestFactory so the POST body is fully buffered and sent.
 * Connect timeout is short (1s); read timeout is generous (2s) because the AI service
 * performs ML prediction + DynamoDB lookup. The Resilience4j circuit breaker handles
 * sustained failures at a higher level.
 */
@Configuration
public class RestTemplateConfig {

    private static final Duration CONNECT_TIMEOUT = Duration.ofMillis(1000);
    private static final Duration READ_TIMEOUT = Duration.ofMillis(2000);

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .requestFactory(() -> new BufferingClientHttpRequestFactory(new SimpleClientHttpRequestFactory()))
                .setConnectTimeout(CONNECT_TIMEOUT)
                .setReadTimeout(READ_TIMEOUT)
                .build();
    }
}
