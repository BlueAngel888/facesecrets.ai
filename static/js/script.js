// Ancient Wisdom Face Analysis - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const paymentBtn = document.getElementById('paymentBtn');
    const freeAnalysisBtn = document.getElementById('freeAnalysisBtn');
    const checkPromoBtn = document.getElementById('checkPromoBtn');
    const promoCodeInput = document.getElementById('promoCode');
    const cameraBtn = document.getElementById('cameraBtn');
    const cameraModal = new bootstrap.Modal(document.getElementById('cameraModal'));
    const camera = document.getElementById('camera');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('captureBtn');
    
    // Debug: Check if elements exist
    console.log('Camera elements found:', {
        cameraBtn: !!cameraBtn,
        camera: !!camera,
        canvas: !!canvas,
        captureBtn: !!captureBtn
    });
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    
    let uploadedFile = false;
    let stream = null;
    let freeAnalysisEnabled = false;
    let guidanceInterval = null;
    let lastGuidanceMessage = '';
    let faceDetectionModel = null;

    // Upload area click handler
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // File input change handler
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Handle file upload
    function handleFile(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
            showAlert('Please select a valid image file (JPEG, PNG, or GIF)', 'danger');
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            showAlert('File size must be less than 16MB', 'danger');
            return;
        }

        // Create FormData and upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', document.querySelector('input[name="language"]').value);

        // Show loading
        loadingModal.show();

        // Upload file
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingModal.hide();
            
            if (data.success) {
                uploadedFile = true;
                updateUploadArea(true, file.name);
                enablePaymentButton();
                showAlert(data.message, 'success');
            } else {
                showAlert(data.error || 'Upload failed', 'danger');
            }
        })
        .catch(error => {
            loadingModal.hide();
            console.error('Upload error:', error);
            showAlert('Upload failed. Please try again.', 'danger');
        });
    }

    // Update upload area appearance
    function updateUploadArea(success, filename) {
        const uploadContent = uploadArea.querySelector('.upload-content');
        
        if (success) {
            uploadArea.classList.add('upload-success');
            uploadContent.innerHTML = `
                <i class="fas fa-check-circle upload-icon"></i>
                <h3>Image Uploaded Successfully!</h3>
                <p>${filename}</p>
                <small>Ready for analysis</small>
            `;
        } else {
            uploadArea.classList.remove('upload-success');
            uploadContent.innerHTML = `
                <i class="fas fa-cloud-upload-alt upload-icon"></i>
                <h3>Upload Photo & Reveal Your Secrets</h3>
                <p>Drop your photo here or click to browse</p>
            `;
        }
    }

    // Enable payment button
    function enablePaymentButton() {
        paymentBtn.disabled = false;
        paymentBtn.innerHTML = '<i class="fas fa-credit-card"></i> Pay 29.99 EUR & Analyze';
    }

    // Payment button click handler
    paymentBtn.addEventListener('click', () => {
        if (!uploadedFile) {
            showAlert('Please upload an image first', 'warning');
            return;
        }

        // Create checkout session
        fetch('/create-checkout-session', {
            method: 'POST'
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            if (data && data.error) {
                showAlert(data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Payment error:', error);
            showAlert('Payment setup failed. Please try again.', 'danger');
        });
    });

    // Camera functionality
    cameraBtn.addEventListener('click', () => {
        startCamera();
    });

    function startCamera() {
        console.log('Starting camera...');
        navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'user',
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        })
        .then(mediaStream => {
            console.log('Camera stream obtained');
            stream = mediaStream;
            camera.srcObject = stream;
            
            // Wait for video to be ready
            camera.onloadedmetadata = () => {
                console.log('Camera metadata loaded');
                camera.play();
                // Start facial guidance after camera is ready
                startFacialGuidance();
                // Setup capture button event listener
                setupCaptureButton();
            };
            
            cameraModal.show();
        })
        .catch(error => {
            console.error('Camera error:', error);
            showAlert('Unable to access camera. Please check permissions.', 'danger');
        });
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        stopFacialGuidance();
    }

    // Smart camera guidance system
    function startFacialGuidance() {
        const guidanceOverlay = document.getElementById('guidanceOverlay');
        const guidanceText = document.getElementById('guidanceText');
        
        if (!guidanceOverlay || !guidanceText) {
            console.warn('Guidance elements not found');
            return;
        }

        guidanceOverlay.style.display = 'block';
        guidanceText.textContent = '📸 Ready to capture! Just position yourself and click the button';

        // Start guidance analysis every 1000ms (less frequent for better performance)
        guidanceInterval = setInterval(() => {
            analyzeFacePosition();
        }, 1000);
    }

    function stopFacialGuidance() {
        if (guidanceInterval) {
            clearInterval(guidanceInterval);
            guidanceInterval = null;
        }
        
        const guidanceOverlay = document.getElementById('guidanceOverlay');
        if (guidanceOverlay) {
            guidanceOverlay.style.display = 'none';
        }
    }

    function analyzeFacePosition() {
        if (!camera || camera.readyState !== 4) return;

        // Create a temporary canvas for analysis
        const analysisCanvas = document.createElement('canvas');
        const ctx = analysisCanvas.getContext('2d');
        
        analysisCanvas.width = camera.videoWidth;
        analysisCanvas.height = camera.videoHeight;
        
        // Draw current frame
        ctx.drawImage(camera, 0, 0);
        
        // Get image data for analysis
        const imageData = ctx.getImageData(0, 0, analysisCanvas.width, analysisCanvas.height);
        
        // Analyze face position and lighting
        const analysis = performFaceAnalysis(imageData, analysisCanvas.width, analysisCanvas.height);
        
        // Update guidance based on analysis
        updateGuidanceMessage(analysis);
    }

    function performFaceAnalysis(imageData, width, height) {
        const data = imageData.data;
        
        // Simple brightness analysis
        let totalBrightness = 0;
        let pixelCount = 0;
        
        // Analyze center region for face presence (simple approximation)
        const centerX = width / 2;
        const centerY = height / 2;
        const regionSize = Math.min(width, height) * 0.3;
        
        let centerBrightness = 0;
        let centerPixels = 0;
        
        for (let y = Math.max(0, centerY - regionSize/2); y < Math.min(height, centerY + regionSize/2); y++) {
            for (let x = Math.max(0, centerX - regionSize/2); x < Math.min(width, centerX + regionSize/2); x++) {
                const index = (y * width + x) * 4;
                const brightness = (data[index] + data[index + 1] + data[index + 2]) / 3;
                
                centerBrightness += brightness;
                centerPixels++;
                totalBrightness += brightness;
                pixelCount++;
            }
        }
        
        const avgBrightness = totalBrightness / pixelCount;
        const avgCenterBrightness = centerBrightness / centerPixels;
        
        // Detect potential face region based on skin tone detection
        const faceRegion = detectFaceRegion(data, width, height);
        
        return {
            brightness: avgBrightness,
            centerBrightness: avgCenterBrightness,
            faceDetected: faceRegion.detected,
            facePosition: faceRegion.position,
            faceSize: faceRegion.size
        };
    }

    function detectFaceRegion(data, width, height) {
        // Very relaxed "face" detection - mostly based on brightness in center area
        let centerPixels = 0;
        let brightPixels = 0;
        let faceX = width / 2;
        let faceY = height / 2;
        
        // Check center area only (much simpler and faster)
        const centerStartX = width * 0.3;
        const centerEndX = width * 0.7;
        const centerStartY = height * 0.3;
        const centerEndY = height * 0.7;
        
        for (let y = centerStartY; y < centerEndY; y += 8) { // Even less frequent sampling
            for (let x = centerStartX; x < centerEndX; x += 8) {
                const index = (y * width + x) * 4;
                const r = data[index];
                const g = data[index + 1];
                const b = data[index + 2];
                
                const brightness = (r + g + b) / 3;
                if (brightness > 60) { // Just check if there's reasonable brightness
                    brightPixels++;
                }
                centerPixels++;
            }
        }
        
        // Very lenient detection - if there's any reasonable content in center, consider it detected
        const detected = brightPixels > centerPixels * 0.3; // 30% of center area has some brightness
        
        return {
            detected: detected,
            position: { x: faceX, y: faceY }, // Always use center
            size: brightPixels * 10 // Fake size that's always reasonable
        };
    }

    function updateGuidanceMessage(analysis) {
        const guidanceText = document.getElementById('guidanceText');
        const captureBtn = document.getElementById('captureBtn');
        const lightingIndicator = document.getElementById('lightingIndicator');
        const faceIndicator = document.getElementById('faceIndicator');
        const sizeIndicator = document.getElementById('sizeIndicator');
        
        if (!guidanceText) return;
        
        let message = '';
        let isReadyToCapture = true;
        
        // Much more relaxed quality indicators - allow almost everything
        updateQualityIndicator(lightingIndicator, 'lightbulb', analysis.brightness >= 50); // More lenient lighting
        updateQualityIndicator(faceIndicator, 'user', analysis.faceDetected || analysis.brightness > 60); // Allow without strict face detection
        updateQualityIndicator(sizeIndicator, 'expand-arrows-alt', true); // Always allow any distance
        
        // Very relaxed guidance - only block in extreme cases
        if (analysis.brightness < 30) {
            message = '💡 Need a bit more light to see you clearly';
            isReadyToCapture = false;
        } else {
            // Always ready to capture in normal conditions
            if (analysis.faceDetected) {
                message = '✅ Looking good! Ready to capture';
            } else {
                message = '📸 Position yourself and capture when ready';
            }
            isReadyToCapture = true;
        }
        
        // Update guidance only if message changed
        if (message !== lastGuidanceMessage) {
            guidanceText.textContent = message;
            lastGuidanceMessage = message;
            
            // Update capture button state and text
            if (captureBtn) {
                const captureText = captureBtn.querySelector('.capture-text');
                if (isReadyToCapture) {
                    captureBtn.classList.remove('btn-warning');
                    captureBtn.classList.add('btn-success');
                    captureBtn.style.animation = 'pulse 1s infinite';
                    if (captureText) captureText.textContent = 'Capture Photo';
                } else {
                    captureBtn.classList.remove('btn-success');
                    captureBtn.classList.add('btn-warning');
                    captureBtn.style.animation = 'none';
                    if (captureText) captureText.textContent = 'Need More Light';
                }
            }
        }
    }

    function updateQualityIndicator(indicator, iconClass, isGood) {
        if (!indicator) return;
        
        const parent = indicator.parentElement;
        
        // Update icon
        indicator.className = `fas fa-${iconClass}`;
        
        // Update indicator status
        parent.className = parent.className.replace(/\b(good|warning|error)\b/g, '');
        parent.classList.add('indicator');
        
        if (isGood) {
            parent.classList.add('good');
        } else {
            parent.classList.add('error');
        }
    }

    // Direct capture button event listener
    function setupCaptureButton() {
        // Wait a bit for modal to fully render
        setTimeout(() => {
            const captureButton = document.getElementById('captureBtn');
            console.log('Setting up capture button:', !!captureButton);
            if (captureButton) {
                // Remove any existing listeners first
                captureButton.replaceWith(captureButton.cloneNode(true));
                const newCaptureButton = document.getElementById('captureBtn');
                
                newCaptureButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Capture button clicked directly');
                    capturePhoto();
                }, { once: false });
                
                console.log('Capture button event listener added');
            }
        }, 500);
    }

    function capturePhoto() {
        console.log('Capturing photo...');
        console.log('Camera ready state:', camera.readyState);
        console.log('Video dimensions:', camera.videoWidth, 'x', camera.videoHeight);
        
        if (camera.readyState !== 4) {
            showAlert('Camera not ready yet. Please wait a moment.', 'warning');
            return;
        }
        
        const context = canvas.getContext('2d');
        canvas.width = camera.videoWidth;
        canvas.height = camera.videoHeight;
        
        // Flip the image back to normal when capturing (since video is mirrored)
        context.save();
        context.scale(-1, 1);
        context.drawImage(camera, -camera.videoWidth, 0);
        context.restore();
        
        canvas.toBlob(blob => {
            console.log('Photo captured, blob size:', blob.size);
            if (blob && blob.size > 0) {
                const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                handleFile(file);
                stopCamera();
                cameraModal.hide();
            } else {
                console.error('Failed to create blob from canvas');
                showAlert('Failed to capture photo. Please try again.', 'danger');
            }
        }, 'image/jpeg', 0.9);
    }
    
    // Global function for inline onclick
    window.capturePhotoNow = function() {
        console.log('Capture button clicked via inline handler');
        capturePhoto();
    };

    // Global click handler for capture button
    document.addEventListener('click', function(e) {
        console.log('Global click on:', e.target.tagName, e.target.id, e.target.className);
        
        // Check if it's the capture button or its children
        if (e.target.id === 'captureBtn' || 
            e.target.closest('#captureBtn') || 
            (e.target.tagName === 'BUTTON' && e.target.textContent.includes('Capture')) ||
            (e.target.tagName === 'SPAN' && e.target.textContent.includes('Capture'))) {
            
            e.preventDefault();
            e.stopPropagation();
            console.log('Capture button detected via global handler');
            capturePhoto();
        }
    }, true); // Use capture phase to catch events early

    // Stop camera when modal is hidden
    document.getElementById('cameraModal').addEventListener('hidden.bs.modal', () => {
        stopCamera();
    });

    // Alert function
    function showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.custom-alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
        alertDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
        `;
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Parallax effect for hero background
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.hero-section::before');
        if (parallax) {
            const speed = scrolled * 0.5;
            parallax.style.transform = `translateY(${speed}px)`;
        }
    });

    // Language switching with fade effect
    const languageLinks = document.querySelectorAll('.dropdown-item[href*="lang="]');
    languageLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            document.body.style.opacity = '0.7';
            setTimeout(() => {
                window.location.href = link.href;
            }, 200);
        });
    });

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe analysis cards
    document.querySelectorAll('.analysis-card, .testimonial-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Promo code functionality
    checkPromoBtn.addEventListener('click', () => {
        const promoCode = promoCodeInput.value.trim();
        
        if (!promoCode) {
            showAlert('Please enter a promo code', 'warning');
            return;
        }

        fetch('/check-promo-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                promo_code: promoCode
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                freeAnalysisEnabled = true;
                freeAnalysisBtn.style.display = 'inline-block';
                paymentBtn.style.display = 'none';
                showAlert(data.message, 'success');
                promoCodeInput.disabled = true;
                checkPromoBtn.disabled = true;
            } else {
                showAlert(data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Promo code error:', error);
            showAlert('Failed to check promo code. Please try again.', 'danger');
        });
    });

    // Free analysis button click handler
    if (freeAnalysisBtn) {
        freeAnalysisBtn.addEventListener('click', () => {
            if (!uploadedFile) {
                showAlert('Please upload an image first', 'warning');
                return;
            }

            if (!freeAnalysisEnabled) {
                showAlert('Free analysis not enabled. Please enter a valid promo code.', 'warning');
                return;
            }

            loadingModal.show();

            fetch('/free-analysis', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                loadingModal.hide();
                if (data.success) {
                    showAlert(data.message, 'success');
                    // Store PDF path for backup download
                    if (data.pdf_path) {
                        localStorage.setItem('pdf_path', data.pdf_path);
                    }
                    // Redirect to results page
                    setTimeout(() => {
                        window.location.href = data.redirect_url || '/success';
                    }, 1500);
                } else {
                    showAlert(data.error || 'Analysis failed', 'danger');
                }
            })
            .catch(error => {
                loadingModal.hide();
                console.error('Free analysis error:', error);
                showAlert('Analysis failed. Please try again.', 'danger');
            });
        });
    }

    // Enable promo code functionality initially
    function enablePromoFeatures() {
        if (uploadedFile) {
            freeAnalysisBtn.disabled = false;
        }
    }

    // Add subtle animations to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Add some mystical particle effects (optional enhancement)
function createParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
        overflow: hidden;
    `;
    
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: 2px;
            height: 2px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            animation: float ${Math.random() * 6 + 4}s ease-in-out infinite;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation-delay: ${Math.random() * 2}s;
        `;
        particleContainer.appendChild(particle);
    }
    
    // Add CSS animation
    if (!document.querySelector('#particle-styles')) {
        const style = document.createElement('style');
        style.id = 'particle-styles';
        style.textContent = `
            @keyframes float {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                33% { transform: translateY(-20px) rotate(120deg); }
                66% { transform: translateY(20px) rotate(240deg); }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(particleContainer);
}

// Initialize particles on hero section
if (document.querySelector('.hero-section')) {
    createParticles();
}
