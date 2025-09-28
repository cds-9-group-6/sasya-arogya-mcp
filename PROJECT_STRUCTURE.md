# Project Structure

```
sasya-arogya-mcp/
├── README.md                    # Main project documentation
├── PROJECT_STRUCTURE.md         # This file - project structure overview
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-container deployment
├── uv.lock                     # UV lock file for dependencies
│
├── mcp_server.py               # Original stdio MCP server
├── mcp_server_simple.py        # Simplified stdio MCP server
├── mcp_http_server.py          # HTTP-based MCP server (main)
│
├── mcp_client.py               # Stdio MCP client
├── mcp_http_client.py          # HTTP MCP client
├── demo_remote.py              # Simple HTTP demo script
│
├── services/                   # Core business logic
│   ├── __init__.py
│   ├── insurance_advisor.py    # Insurance recommendation logic
│   ├── insurance_certificate.py # PDF certificate generation
│   ├── crop_premium.py         # Premium calculation
│   ├── insurance_companies.py  # Company data management
│   └── pdf_generator.py        # PDF generation utilities
│
├── resources/                  # Data files
│   ├── crop_data.csv          # Crop and premium data
│   ├── insurance_companies.csv # Insurance company data
│   └── india_logo.jpg         # Government logo for certificates
│
├── templates/                  # HTML templates
│   └── insurance_template.html # Certificate template
│
└── clients/                    # Legacy client code
    ├── mcp_client.py           # Original HTTP client
    └── insurance_certificate.pdf # Sample output
```

## Key Files Explained

### 🚀 Server Files
- **`mcp_http_server.py`** - Main production server (HTTP-based)
- **`mcp_server_simple.py`** - Simplified stdio server for development
- **`mcp_server.py`** - Original stdio server (legacy)

### 🧪 Client Files
- **`mcp_http_client.py`** - Async HTTP client for testing
- **`demo_remote.py`** - Simple HTTP demo with requests library
- **`mcp_client.py`** - Stdio MCP client for local testing

### 🛠️ Services
- **`insurance_advisor.py`** - AI-powered insurance recommendations
- **`insurance_certificate.py`** - PDF certificate generation with ReportLab
- **`crop_premium.py`** - Premium calculation based on crop data
- **`insurance_companies.py`** - Insurance company data management
- **`pdf_generator.py`** - Generic PDF generation utilities

### 📊 Data Files
- **`crop_data.csv`** - Crop information and premium rates
- **`insurance_companies.csv`** - Insurance company directory
- **`india_logo.jpg`** - Government logo for certificates

### 🐳 Deployment
- **`Dockerfile`** - Container configuration
- **`docker-compose.yml`** - Multi-container deployment
- **`requirements.txt`** - Python dependencies

## Development Workflow

### 1. Local Development
```bash
# Start stdio server
python3 mcp_server_simple.py

# Test with stdio client
python3 mcp_client.py
```

### 2. Remote Development
```bash
# Start HTTP server
python3 mcp_http_server.py --port 8000

# Test with HTTP client
python3 mcp_http_client.py

# Or simple demo
python3 demo_remote.py
```

### 3. Production Deployment
```bash
# Docker
docker build -t sasya-arogya-mcp .
docker run -p 8000:8000 sasya-arogya-mcp

# Docker Compose
docker-compose up -d
```

## Architecture Patterns

### MCP Protocol
- **Stdio Mode**: Process-to-process communication
- **HTTP Mode**: REST API for remote access
- **Streaming**: Server-Sent Events for real-time data

### Service Layer
- **Business Logic**: Separated into service modules
- **Data Access**: CSV-based data storage
- **PDF Generation**: ReportLab for professional output

### Container Design
- **Multi-stage Build**: Optimized for production
- **Non-root User**: Security best practices
- **Health Checks**: Container orchestration support
- **Volume Mounting**: Data persistence

## Testing Strategy

### Unit Tests
- Individual service functions
- Data validation and processing
- Error handling scenarios

### Integration Tests
- End-to-end MCP tool execution
- HTTP API functionality
- PDF generation verification

### Load Tests
- Concurrent request handling
- Memory and CPU usage
- Response time benchmarks

## Security Considerations

### Container Security
- Non-root user execution
- Minimal base image
- Resource limits
- Network isolation

### API Security
- Input validation with Pydantic
- CORS configuration
- Error handling without information leakage
- Rate limiting (future enhancement)

## Performance Optimization

### Code Level
- Async/await for concurrency
- Connection pooling
- Memory-efficient data processing
- Caching strategies

### Infrastructure Level
- Container resource limits
- Horizontal scaling
- Load balancing
- CDN for static assets

## Monitoring & Observability

### Health Checks
- Application health endpoint
- Container health checks
- Load balancer integration

### Logging
- Structured JSON logging
- Request/response tracking
- Error monitoring
- Performance metrics

### Metrics
- Request count and duration
- Error rates
- Resource utilization
- Business metrics (premiums calculated, certificates generated)
