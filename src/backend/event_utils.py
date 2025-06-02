import logging
import os

# Thought into existence by Darbot - Fix Azure Monitor import issue
try:
    # Try importing from azure-monitor-opentelemetry-exporter 
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    AZURE_MONITOR_AVAILABLE = True
except ImportError:
    AZURE_MONITOR_AVAILABLE = False
    logging.warning("Azure Monitor OpenTelemetry exporter not available")


def track_event_if_configured(event_name: str, event_data: dict):
    """Track an event if Application Insights is configured.

    This function safely wraps Azure Monitor functionality to track events.
    Falls back gracefully if Azure Monitor is not available.

    Args:
        event_name: The name of the event to track
        event_data: Dictionary of event data/dimensions
    """
    try:
        instrumentation_key = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        if instrumentation_key and AZURE_MONITOR_AVAILABLE:
            # Use OpenTelemetry to track events
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(event_name) as span:
                for key, value in event_data.items():
                    span.set_attribute(key, str(value))
                logging.info(f"Tracked event: {event_name} with data: {event_data}")
        else:
            # Just log the event if Azure Monitor is not configured or available
            logging.info(f"Event tracking (not configured): {event_name} - {event_data}")
    except Exception as e:
        # Catch any exceptions to prevent them from bubbling up
        logging.warning(f"Error in track_event: {e}")
        # Still log the event for debugging
        logging.info(f"Event (fallback): {event_name} - {event_data}")
