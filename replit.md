# Overview

A Flask-based web application that provides a REST API for image generation, text generation, and image analysis using OpenAI's APIs. The application features a simple web interface with comprehensive API documentation and supports DALL-E 3 image generation, GPT text generation, and GPT-4o Vision for image analysis. Built with a minimalist architecture focusing on ease of use and integration, with optional proxy support for OpenAI requests.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates for server-side rendering
- **Styling Framework**: Bootstrap 5 with dark theme and custom CSS overlays
- **UI Components**: Single-page documentation interface with glassmorphism design
- **Icons**: Font Awesome for visual elements

## Backend Architecture
- **Web Framework**: Flask with minimal configuration and CORS support
- **API Design**: RESTful endpoints for image generation, text generation, and image analysis:
  - `/api/generate-image` - DALL-E 3 image generation using POST method
  - `/api/generate-text` - GPT text generation and image analysis using POST method
    - Text mode: GPT-4, GPT-4-turbo, GPT-3.5-turbo
    - Image analysis mode: GPT-4o (auto-switched when image_url provided)
- **Request Handling**: JSON payload processing with comprehensive error handling
- **Response Format**: Standardized JSON responses with success/error states and usage metrics
- **Proxy Support**: Optional HTTP proxy configuration specifically for OpenAI API requests
- **Logging**: Python's built-in logging module for debugging and monitoring

## Configuration Management
- **Environment Variables**: 
  - `OPENAI_API_KEY` - Required for both image and text generation
  - `OPENAI_PROXY` - Optional HTTP proxy for OpenAI requests only
- **Error Handling**: Graceful degradation when API key is not configured
- **Development Mode**: Debug mode enabled for local development
- **Proxy Configuration**: Selective proxy usage only for OpenAI API calls, other requests use direct connection

## Security Considerations
- **Session Management**: Flask session secret for potential future authentication
- **API Key Protection**: Environment variable-based API key storage
- **Input Validation**: JSON payload validation for image generation requests

# External Dependencies

## Core Dependencies
- **Flask**: Web framework for HTTP server and routing
- **OpenAI Python Client**: Official SDK for DALL-E API integration

## Frontend Dependencies
- **Bootstrap 5**: CSS framework loaded via CDN with dark theme
- **Font Awesome 6**: Icon library loaded via CDN
- **Custom CSS**: Glassmorphism effects and gradient styling

## External Services
- **OpenAI DALL-E API**: Primary image generation service
- **CDN Services**: Bootstrap and Font Awesome asset delivery

## Development Infrastructure
- **Python Logging**: Built-in logging for application monitoring
- **Environment Configuration**: OS environment variable management
- **Static File Serving**: Flask's built-in static file handler