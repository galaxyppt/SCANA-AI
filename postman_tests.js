// Test script to be added in Postman's "Tests" tab
const fs = require('fs');
const path = require('path');

// Save response to file
const filePath = path.join(__dirname, 'postman_delivery_data.json');
fs.writeFileSync(filePath, JSON.stringify(pm.response.json(), null, 2));

// Verify response format
pm.test("Response has correct format", function () {
    const response = pm.response.json();
    
    // Function to validate delivery object
    function validateDelivery(delivery) {
        pm.expect(delivery).to.have.property('vendor_name');
        pm.expect(delivery).to.have.property('delivery_date');
        pm.expect(delivery).to.have.property('delivery_time');
        pm.expect(delivery).to.have.property('delivery_temperature');
        pm.expect(delivery).to.have.property('product_quality_score');
        
        // Validate temperature range
        pm.expect(delivery.delivery_temperature).to.be.within(2.0, 8.0);
        
        // Validate quality score range
        pm.expect(delivery.product_quality_score).to.be.within(75.0, 100.0);
    }
    
    // Check if response is array or single object
    if (Array.isArray(response)) {
        response.forEach(validateDelivery);
    } else {
        validateDelivery(response);
    }
});

// SCANA-AI API Test Suite

// Helper functions
function validateDeliveryData(data) {
    pm.expect(data).to.be.an('object');
    pm.expect(data).to.have.property('vendor_name');
    pm.expect(data).to.have.property('delivery_date');
    pm.expect(data).to.have.property('delivery_time');
    pm.expect(data).to.have.property('delivery_temperature');
    pm.expect(data).to.have.property('product_quality_score');
    
    // Validate temperature range
    pm.expect(data.delivery_temperature).to.be.within(2.0, 8.0);
    
    // Validate quality score range
    pm.expect(data.product_quality_score).to.be.within(75.0, 100.0);
    
    // Validate date format
    pm.expect(data.delivery_date).to.match(/^\d{4}-\d{2}-\d{2}$/);
    
    // Validate time format
    pm.expect(data.delivery_time).to.match(/^\d{2}:\d{2}$/);
}

function validateSLACompliance(data) {
    const violations = [];
    
    // Check temperature compliance
    if (data.delivery_temperature < 2.0 || data.delivery_temperature > 8.0) {
        violations.push({
            type: 'temperature',
            value: data.delivery_temperature,
            threshold: '2.0-8.0°C'
        });
    }
    
    // Check quality compliance
    if (data.product_quality_score < 85) {
        violations.push({
            type: 'quality',
            value: data.product_quality_score,
            threshold: '85'
        });
    }
    
    return violations;
}

// Test Suites
pm.test("Response status code is 200", () => {
    pm.response.to.have.status(200);
});

pm.test("Response has valid structure", () => {
    const response = pm.response.json();
    pm.expect(response).to.have.property('status');
    pm.expect(response.status).to.eql('success');
    pm.expect(response).to.have.property('data');
});

if (pm.request.url.path.includes('/deliveries/batch')) {
    pm.test("Batch delivery data is valid", () => {
        const response = pm.response.json();
        pm.expect(response.data).to.be.an('array');
        response.data.forEach(delivery => {
            validateDeliveryData(delivery);
            const violations = validateSLACompliance(delivery);
            pm.expect(violations, `SLA violations found: ${JSON.stringify(violations)}`).to.be.empty;
        });
    });
} else if (pm.request.url.path.includes('/deliveries')) {
    pm.test("Single delivery data is valid", () => {
        const response = pm.response.json();
        validateDeliveryData(response.data);
        const violations = validateSLACompliance(response.data);
        pm.expect(violations, `SLA violations found: ${JSON.stringify(violations)}`).to.be.empty;
    });
} 