import React, { useEffect, useRef } from 'react';

const Particles = ({ count = 50 }) => {
  const containerRef = useRef(null);
  const particlesRef = useRef([]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const particles = [];
    const particleElements = [];

    for (let i = 0; i < count; i++) {
      const particle = {
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 3 + 1,
        speedX: (Math.random() - 0.5) * 0.2,
        speedY: (Math.random() - 0.5) * 0.2,
        opacity: Math.random() * 0.5 + 0.3,
        pulseSpeed: Math.random() * 0.02 + 0.01,
        pulseOffset: Math.random() * Math.PI * 2,
      };

      const element = document.createElement('div');
      element.className = 'particle';
      element.style.left = `${particle.x}%`;
      element.style.top = `${particle.y}%`;
      element.style.width = `${particle.size}px`;
      element.style.height = `${particle.size}px`;
      element.style.opacity = particle.opacity;
      element.style.animationDelay = `${Math.random() * 5}s`;
      
      container.appendChild(element);
      particles.push(particle);
      particleElements.push(element);
    }

    particlesRef.current = particles;

    let animationFrameId;
    let time = 0;

    const animate = () => {
      time += 1;
      
      particles.forEach((particle, index) => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;

        if (particle.x < 0) particle.x = 100;
        if (particle.x > 100) particle.x = 0;
        if (particle.y < 0) particle.y = 100;
        if (particle.y > 100) particle.y = 0;

        const pulse = Math.sin(time * particle.pulseSpeed + particle.pulseOffset) * 0.3 + 0.7;
        
        particleElements[index].style.left = `${particle.x}%`;
        particleElements[index].style.top = `${particle.y}%`;
        particleElements[index].style.opacity = particle.opacity * pulse;
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    const handleMouseMove = (e) => {
      const rect = container.getBoundingClientRect();
      const mouseX = ((e.clientX - rect.left) / rect.width) * 100;
      const mouseY = ((e.clientY - rect.top) / rect.height) * 100;

      particles.forEach((particle, index) => {
        const dx = mouseX - particle.x;
        const dy = mouseY - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 20) {
          const force = (20 - distance) / 20;
          particle.speedX += (dx / distance) * force * 0.1;
          particle.speedY += (dy / distance) * force * 0.1;
        }

        particle.speedX *= 0.99;
        particle.speedY *= 0.99;

        const minSpeed = 0.02;
        if (Math.abs(particle.speedX) < minSpeed) {
          particle.speedX = particle.speedX > 0 ? minSpeed : -minSpeed;
        }
        if (Math.abs(particle.speedY) < minSpeed) {
          particle.speedY = particle.speedY > 0 ? minSpeed : -minSpeed;
        }
      });
    };

    container.addEventListener('mousemove', handleMouseMove);

    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener('mousemove', handleMouseMove);
      particleElements.forEach(element => element.remove());
    };
  }, [count]);

  return <div ref={containerRef} className="particles-container" />;
};

export default Particles;
