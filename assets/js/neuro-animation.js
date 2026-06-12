/**
 * Neuro-Animation JS
 * A dynamic neural network animation using HTML5 Canvas.
 * Optimized for Juan Moisés de la Serna's Research Identity 10.0 theme.
 */

class NeuroAnimation {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };
        this.numberOfParticles = 80;
        this.connectionDistance = 120;

        this.init();
        this.animate();

        window.addEventListener('resize', () => {
            this.resize();
        });

        this.canvas.addEventListener('mousemove', (event) => {
            const rect = this.canvas.getBoundingClientRect();
            this.mouse.x = event.clientX - rect.left;
            this.mouse.y = event.clientY - rect.top;
        });

        this.canvas.addEventListener('mouseleave', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });
    }

    getColors() {
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        return {
            particle: isDark ? '#38bdf8' : '#0066cc',
            line: isDark ? 'rgba(56, 189, 248,' : 'rgba(0, 102, 204,',
            pulse: isDark ? '#00d1b2' : '#6e5494'
        };
    }

    resize() {
        this.canvas.width = this.canvas.parentElement.offsetWidth;
        this.canvas.height = this.canvas.parentElement.offsetHeight || 400;
        this.numberOfParticles = Math.floor((this.canvas.width * this.canvas.height) / 10000);
        this.init();
    }

    init() {
        this.canvas.width = this.canvas.parentElement.offsetWidth;
        this.canvas.height = this.canvas.parentElement.offsetHeight || 400;
        this.particles = [];
        for (let i = 0; i < this.numberOfParticles; i++) {
            const size = Math.random() * 2 + 1;
            const x = Math.random() * (this.canvas.width - size * 2) + size;
            const y = Math.random() * (this.canvas.height - size * 2) + size;
            const directionX = (Math.random() * 0.4) - 0.2;
            const directionY = (Math.random() * 0.4) - 0.2;
            this.particles.push(new Particle(x, y, directionX, directionY, size));
        }
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const colors = this.getColors();

        for (let i = 0; i < this.particles.length; i++) {
            this.particles[i].update(this.canvas);
            this.particles[i].draw(this.ctx, colors.particle);
        }
        this.connect(colors);
    }

    connect(colors) {
        for (let a = 0; a < this.particles.length; a++) {
            for (let b = a; b < this.particles.length; b++) {
                const dx = this.particles[a].x - this.particles[b].x;
                const dy = this.particles[a].y - this.particles[b].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.connectionDistance) {
                    let opacity = 1 - (distance / this.connectionDistance);
                    this.ctx.strokeStyle = colors.line + opacity + ')';
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[a].x, this.particles[a].y);
                    this.ctx.lineTo(this.particles[b].x, this.particles[b].y);
                    this.ctx.stroke();

                    // Neural Pulse (Action Potential)
                    if (Math.random() > 0.995) {
                        this.drawPulse(this.particles[a], this.particles[b], colors.pulse);
                    }
                }
            }

            // Mouse Interaction
            if (this.mouse.x !== null) {
                const dx = this.particles[a].x - this.mouse.x;
                const dy = this.particles[a].y - this.mouse.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < this.mouse.radius) {
                    this.ctx.strokeStyle = colors.line + (1 - distance/this.mouse.radius) + ')';
                    this.ctx.lineWidth = 2;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[a].x, this.particles[a].y);
                    this.ctx.lineTo(this.mouse.x, this.mouse.y);
                    this.ctx.stroke();
                }
            }
        }
    }

    drawPulse(p1, p2, color) {
        const time = (Date.now() % 1000) / 1000;
        const x = p1.x + (p2.x - p1.x) * time;
        const y = p1.y + (p2.y - p1.y) * time;
        this.ctx.fillStyle = color;
        this.ctx.beginPath();
        this.ctx.arc(x, y, 2, 0, Math.PI * 2);
        this.ctx.fill();
    }
}

class Particle {
    constructor(x, y, directionX, directionY, size) {
        this.x = x;
        this.y = y;
        this.directionX = directionX;
        this.directionY = directionY;
        this.size = size;
    }

    draw(ctx, color) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
    }

    update(canvas) {
        if (this.x > canvas.width || this.x < 0) this.directionX = -this.directionX;
        if (this.y > canvas.height || this.y < 0) this.directionY = -this.directionY;
        this.x += this.directionX;
        this.y += this.directionY;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('neuroCanvas')) {
        new NeuroAnimation('neuroCanvas');
    }
});
