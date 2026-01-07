/**
 * PrimeHaul OS - ML Data Collection Tracker
 *
 * Automatically tracks all user interactions for machine learning training.
 * Captures: page views, clicks, scrolls, form inputs, time on page, etc.
 *
 * Usage: Include this script on ALL customer-facing pages
 * <script src="/static/tracker.js"></script>
 */

(function() {
    'use strict';

    // Configuration
    const TRACKER_CONFIG = {
        endpoint: '/api/track',
        throttleMs: 1000,  // Don't send more than once per second
        debug: false       // Set to true for console logging
    };

    // Session management
    let sessionId = localStorage.getItem('ph_session_id');
    if (!sessionId) {
        sessionId = generateId();
        localStorage.setItem('ph_session_id', sessionId);
    }

    // Page load time tracking
    const pageLoadTime = Date.now();
    let lastScrollTime = Date.now();
    let maxScrollDepth = 0;

    // Extract job token from URL if present
    const jobToken = extractJobToken();

    /**
     * Generate unique ID
     */
    function generateId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    /**
     * Extract job token from URL
     */
    function extractJobToken() {
        const match = window.location.pathname.match(/\/s\/[^\/]+\/([^\/]+)/);
        return match ? match[1] : null;
    }

    /**
     * Send tracking event to backend
     */
    function sendEvent(data) {
        try {
            const formData = new FormData();
            formData.append('event_type', data.event_type);
            formData.append('page_url', window.location.pathname);
            formData.append('session_id', sessionId);

            if (jobToken) {
                formData.append('job_token', jobToken);
            }

            // Optional fields
            if (data.element_id) formData.append('element_id', data.element_id);
            if (data.element_text) formData.append('element_text', data.element_text);
            if (data.time_spent_seconds !== undefined) formData.append('time_spent_seconds', data.time_spent_seconds);
            if (data.scroll_depth_percent !== undefined) formData.append('scroll_depth_percent', data.scroll_depth_percent);

            // Screen dimensions
            formData.append('screen_width', window.screen.width);
            formData.append('screen_height', window.screen.height);

            // Additional metadata
            if (data.metadata) {
                formData.append('metadata', JSON.stringify(data.metadata));
            }

            // Send asynchronously (don't wait for response)
            fetch(TRACKER_CONFIG.endpoint, {
                method: 'POST',
                body: formData,
                keepalive: true  // Keep request alive even if user navigates away
            }).catch(err => {
                if (TRACKER_CONFIG.debug) {
                    console.error('Tracking error:', err);
                }
            });

            if (TRACKER_CONFIG.debug) {
                console.log('📊 Tracked:', data.event_type, data);
            }
        } catch (err) {
            // Silently fail - don't break user experience
            if (TRACKER_CONFIG.debug) {
                console.error('Tracking error:', err);
            }
        }
    }

    /**
     * Track page view
     */
    function trackPageView() {
        sendEvent({
            event_type: 'page_view',
            metadata: {
                referrer: document.referrer,
                title: document.title
            }
        });
    }

    /**
     * Track click
     */
    function trackClick(event) {
        const element = event.target;
        const elementId = element.id || element.className || element.tagName;
        const elementText = element.textContent ? element.textContent.slice(0, 100) : '';

        sendEvent({
            event_type: 'click',
            element_id: elementId,
            element_text: elementText,
            metadata: {
                tag: element.tagName,
                href: element.href || null
            }
        });
    }

    /**
     * Track scroll (throttled)
     */
    const trackScroll = throttle(function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;

        const scrollPercent = Math.round((scrollTop / (documentHeight - windowHeight)) * 100) || 0;

        // Track max scroll depth
        if (scrollPercent > maxScrollDepth) {
            maxScrollDepth = scrollPercent;

            sendEvent({
                event_type: 'scroll',
                scroll_depth_percent: scrollPercent
            });
        }
    }, TRACKER_CONFIG.throttleMs);

    /**
     * Track form input
     */
    const trackInput = throttle(function(event) {
        const element = event.target;

        // Don't track actual passwords/sensitive data
        if (element.type === 'password') return;

        sendEvent({
            event_type: 'input',
            element_id: element.id || element.name,
            metadata: {
                field_name: element.name,
                field_type: element.type,
                value_length: element.value ? element.value.length : 0  // Length only, not actual value
            }
        });
    }, TRACKER_CONFIG.throttleMs);

    /**
     * Track page exit (time spent)
     */
    function trackPageExit() {
        const timeSpent = (Date.now() - pageLoadTime) / 1000;  // Convert to seconds

        // Use sendBeacon for reliability on page unload
        const data = new FormData();
        data.append('event_type', 'page_exit');
        data.append('page_url', window.location.pathname);
        data.append('session_id', sessionId);
        data.append('time_spent_seconds', timeSpent);
        data.append('scroll_depth_percent', maxScrollDepth);
        data.append('screen_width', window.screen.width);
        data.append('screen_height', window.screen.height);

        if (jobToken) {
            data.append('job_token', jobToken);
        }

        navigator.sendBeacon(TRACKER_CONFIG.endpoint, data);
    }

    /**
     * Track photo upload (custom event)
     */
    window.trackPhotoUpload = function(success, photoCount, totalSize) {
        sendEvent({
            event_type: 'photo_upload',
            metadata: {
                success: success,
                photo_count: photoCount,
                total_size_bytes: totalSize
            }
        });
    };

    /**
     * Track error (custom event)
     */
    window.trackError = function(errorMessage) {
        sendEvent({
            event_type: 'error',
            metadata: {
                error: errorMessage,
                url: window.location.href
            }
        });
    };

    /**
     * Throttle function
     */
    function throttle(func, wait) {
        let timeout;
        let previous = 0;

        return function() {
            const now = Date.now();
            const remaining = wait - (now - previous);
            const context = this;
            const args = arguments;

            if (remaining <= 0 || remaining > wait) {
                if (timeout) {
                    clearTimeout(timeout);
                    timeout = null;
                }
                previous = now;
                func.apply(context, args);
            } else if (!timeout) {
                timeout = setTimeout(function() {
                    previous = Date.now();
                    timeout = null;
                    func.apply(context, args);
                }, remaining);
            }
        };
    }

    // ============================================================================
    // ATTACH EVENT LISTENERS
    // ============================================================================

    // Track page view on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', trackPageView);
    } else {
        trackPageView();
    }

    // Track clicks
    document.addEventListener('click', trackClick);

    // Track scrolls (throttled)
    window.addEventListener('scroll', trackScroll);

    // Track form inputs (throttled)
    document.addEventListener('input', trackInput);

    // Track page exit (time spent)
    window.addEventListener('beforeunload', trackPageExit);
    window.addEventListener('pagehide', trackPageExit);  // Mobile Safari

    // Track visibility changes (tab switching)
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            sendEvent({
                event_type: 'tab_hidden',
                time_spent_seconds: (Date.now() - pageLoadTime) / 1000
            });
        } else {
            sendEvent({
                event_type: 'tab_visible'
            });
        }
    });

    // Track errors
    window.addEventListener('error', function(event) {
        sendEvent({
            event_type: 'js_error',
            metadata: {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno
            }
        });
    });

    // Expose API for custom tracking
    window.PrimeHaulTracker = {
        track: sendEvent,
        trackPhotoUpload: window.trackPhotoUpload,
        trackError: window.trackError,
        sessionId: sessionId,
        debug: function(enabled) {
            TRACKER_CONFIG.debug = enabled;
        }
    };

    if (TRACKER_CONFIG.debug) {
        console.log('📊 PrimeHaul Tracker initialized', {
            sessionId: sessionId,
            jobToken: jobToken,
            page: window.location.pathname
        });
    }

})();
