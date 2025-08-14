# Overview

A Flask-based web application that provides a REST API for generating images using OpenAI's DALL-E API. The application features a simple web interface with API documentation and a single endpoint that accepts text prompts and returns generated image URLs. Built with a minimalist architecture focusing on ease of use and integration.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates for server-side rendering
- **Styling Framework**: Bootstrap 5 with dark theme and custom CSS overlays
- **UI Components**: Single-page documentation interface with glassmorphism design
- **Icons**: Font Awesome for visual elements

## Backend Architecture
- **Web Framework**: Flask with minimal configuration
- **API Design**: RESTful single endpoint (`/api/generate-image`) using POST method
- **Request Handling**: JSON payload processing with error handling
- **Response Format**: Standardized JSON responses with success/error states
- **Logging**: Python's built-in logging module for debugging and monitoring

## Configuration Management
- **Environment Variables**: OpenAI API key and session secret management
- **Error Handling**: Graceful degradation when API key is not configured
- **Development Mode**: Debug mode enabled for local development

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