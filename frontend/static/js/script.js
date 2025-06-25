// Main JavaScript for the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any global functionality
    
    // Mobile menu toggle (if needed)
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
        });
    }
    
    // Flash message auto-close
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });
    
    // Date picker initialization for booking page
    const bookingDate = document.getElementById('booking-date');
    if (bookingDate) {
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        bookingDate.setAttribute('min', today);
    }
});

// API functions
async function fetchTimeSlots(counterId, date) {
    try {
        const response = await fetch(`/api/time_slots?counter_id=${counterId}&date=${date}`);
        if (!response.ok) {
            throw new Error('Failed to fetch time slots');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching time slots:', error);
        return [];
    }
}

async function createBooking(bookingData) {
    try {
        const response = await fetch('/api/bookings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookingData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to create booking');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error creating booking:', error);
        return null;
    }
}