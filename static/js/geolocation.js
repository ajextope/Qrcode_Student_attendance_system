// Geolocation utility functions for QR Attendance System

/**
 * Get current user location with promise-based API
 * @param {Function} successCallback - Function to call on success with position object
 * @param {Function} errorCallback - Function to call on error with error message
 */
function getCurrentLocation(successCallback, errorCallback) {
    if (!navigator.geolocation) {
        errorCallback("Geolocation is not supported by your browser");
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            successCallback({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            });
        },
        function(error) {
            let errorMessage;
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage = "User denied the request for geolocation";
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage = "Location information is unavailable";
                    break;
                case error.TIMEOUT:
                    errorMessage = "The request to get user location timed out";
                    break;
                case error.UNKNOWN_ERROR:
                    errorMessage = "An unknown error occurred";
                    break;
            }
            errorCallback(errorMessage);
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

/**
 * Calculate distance between two points using Haversine formula
 * @param {number} lat1 - Latitude of first point
 * @param {number} lon1 - Longitude of first point
 * @param {number} lat2 - Latitude of second point
 * @param {number} lon2 - Longitude of second point
 * @returns {number} Distance in meters
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const d = R * c;
    
    return d; // Distance in meters
}

/**
 * Check if a point is within a radius of another point
 * @param {number} userLat - User's latitude
 * @param {number} userLon - User's longitude
 * @param {number} locationLat - Location's latitude
 * @param {number} locationLon - Location's longitude
 * @param {number} radius - Maximum allowed distance in meters
 * @returns {boolean} True if within radius, false otherwise
 */
function isWithinRadius(userLat, userLon, locationLat, locationLon, radius) {
    const distance = calculateDistance(userLat, userLon, locationLat, locationLon);
    return distance <= radius;
}
