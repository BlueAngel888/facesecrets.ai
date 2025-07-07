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
        guidanceText.textContent = 'Position your face in the center of the frame';

        // Start guidance analysis every 500ms
        guidanceInterval = setInterval(() => {
            analyzeFacePosition();
        }, 500);
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
        // Simple skin tone detection
        let skinPixels = 0;
        let totalPixels = 0;
        let faceX = 0, faceY = 0;
        
        for (let y = 0; y < height; y += 4) { // Sample every 4th pixel for performance
            for (let x = 0; x < width; x += 4) {
                const index = (y * width + x) * 4;
                const r = data[index];
                const g = data[index + 1];
                const b = data[index + 2];
                
                // Simple skin tone detection
                if (isSkinTone(r, g, b)) {
                    skinPixels++;
                    faceX += x;
                    faceY += y;
                }
                totalPixels++;
            }
        }
        
        const skinRatio = skinPixels / totalPixels;
        const detected = skinRatio > 0.05; // At least 5% skin tone pixels
        
        return {
            detected: detected,
            position: detected ? {
                x: faceX / skinPixels,
                y: faceY / skinPixels
            } : { x: width/2, y: height/2 },
            size: skinPixels
        };
    }

    function isSkinTone(r, g, b) {
        // Enhanced skin tone detection algorithm
        return (r > 95 && g > 40 && b > 20 && 
                Math.max(r, g, b) - Math.min(r, g, b) > 15 &&
                Math.abs(r - g) > 15 && r > g && r > b);
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
        
        // Update quality indicators
        updateQualityIndicator(lightingIndicator, 'lightbulb', analysis.brightness >= 80 && analysis.brightness <= 200);
        updateQualityIndicator(faceIndicator, 'user', analysis.faceDetected);
        updateQualityIndicator(sizeIndicator, 'expand-arrows-alt', analysis.faceSize >= 500 && analysis.faceSize <= 2000);
        
        // Lighting guidance
        if (analysis.brightness < 80) {
            message = '💡 Move to a brighter area or turn on more lights';
            isReadyToCapture = false;
        } else if (analysis.brightness > 200) {
            message = '☀️ Too bright! Move away from direct light or reduce lighting';
            isReadyToCapture = false;
        }
        
        // Face detection guidance
        else if (!analysis.faceDetected) {
            message = '👤 Please position your face in the center of the frame';
            isReadyToCapture = false;
        }
        
        // Face positioning guidance
        else if (analysis.faceDetected) {
            const centerX = camera.videoWidth / 2;
            const centerY = camera.videoHeight / 2;
            const faceX = analysis.facePosition.x;
            const faceY = analysis.facePosition.y;
            
            const offsetX = Math.abs(faceX - centerX);
            const offsetY = Math.abs(faceY - centerY);
            
            if (offsetX > camera.videoWidth * 0.15) {
                message = faceX < centerX ? '⬅️ Move slightly to the left' : '➡️ Move slightly to the right';
                isReadyToCapture = false;
            } else if (offsetY > camera.videoHeight * 0.15) {
                message = faceY < centerY ? '⬆️ Move slightly up' : '⬇️ Move slightly down';
                isReadyToCapture = false;
            } else if (analysis.faceSize < 500) {
                message = '🔍 Move closer to the camera';
                isReadyToCapture = false;
            } else if (analysis.faceSize > 2000) {
                message = '📏 Move back a little - you\'re too close';
                isReadyToCapture = false;
            } else {
                message = '✅ Perfect! Ready to capture';
                isReadyToCapture = true;
            }
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
                    if (captureText) captureText.textContent = 'Capture Perfect Shot!';
                } else {
                    captureBtn.classList.remove('btn-success');
                    captureBtn.classList.add('btn-warning');
                    captureBtn.style.animation = 'none';
                    if (captureText) captureText.textContent = 'Adjust Position';
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

    // Capture photo - Use event delegation to handle dynamically loaded content
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'captureBtn') {
            console.log('Capture button clicked');
            console.log('Camera ready state:', camera.readyState);
            console.log('Video dimensions:', camera.videoWidth, 'x', camera.videoHeight);
            
            if (camera.readyState !== 4) {
                showAlert('Camera not ready yet. Please wait a moment.', 'warning');
                return;
            }
            
            const context = canvas.getContext('2d');
            canvas.width = camera.videoWidth;
            canvas.height = camera.videoHeight;
            context.drawImage(camera, 0, 0);
            
            canvas.toBlob(blob => {
                console.log('Photo captured, blob size:', blob.size);
                const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                handleFile(file);
                stopCamera();
                cameraModal.hide();
            }, 'image/jpeg', 0.9);
        }
    });

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
