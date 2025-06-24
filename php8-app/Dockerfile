# syntax=docker/dockerfile:1.4

# --- Stage 1: Install PHP dependencies using Composer ---
FROM --platform=$BUILDPLATFORM composer:2 as composer

WORKDIR /app
COPY composer.json ./
RUN composer install --no-dev --optimize-autoloader

COPY . /app

# --- Stage 2: Build final PHP8 FPM image ---
FROM --platform=$TARGETPLATFORM php:8.2-fpm-alpine

# Install required system dependencies and PHP extensions
RUN apk add --no-cache postgresql-dev libpq $PHPIZE_DEPS \
    && docker-php-ext-install pdo pdo_pgsql \
    && pecl install redis \
    && docker-php-ext-enable redis \
    && rm -rf /var/cache/apk/*

WORKDIR /var/www/html
COPY --from=composer /app /var/www/html

# Set proper permissions for non-root usage
RUN chown -R www-data:www-data /var/www/html

# Healthcheck: make sure php-fpm is running
HEALTHCHECK CMD pgrep php-fpm || exit 1

# Environment variables for runtime configuration
ENV APP_ENV=production \
    DB_HOST=postgres \
    DB_PORT=5432 \
    DB_USER=appuser \
    DB_PASSWORD=apppass \
    REDIS_HOST=redis \
    REDIS_PORT=6379

EXPOSE 9000
USER www-data
CMD ["php-fpm", "-F"]

# Notes:
# - This image is intended to be used with a separate web server container (nginx or apache).
# - It includes all PHP dependencies for communicating with PostgreSQL and Redis.
