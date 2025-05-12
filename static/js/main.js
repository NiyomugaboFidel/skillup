
document.addEventListener('DOMContentLoaded', () => {
  // Desktop course dropdown
  const desktopCourseBtn = document.getElementById('desktop-course-btn');
  const desktopCourseMenu = document.getElementById('desktop-course-menu');

  desktopCourseBtn.addEventListener('click', () => {
    desktopCourseMenu.classList.toggle('hidden');
  });

  // Close desktop dropdown when clicking outside
  document.addEventListener('click', (event) => {
    if (!desktopCourseBtn.contains(event.target) && !desktopCourseMenu.contains(event.target)) {
      desktopCourseMenu.classList.add('hidden');
    }
  });

  // Mobile menu toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const menuOpenIcon = document.getElementById('menu-open-icon');
  const menuCloseIcon = document.getElementById('menu-close-icon');

  mobileMenuBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
    menuOpenIcon.classList.toggle('hidden');
    menuCloseIcon.classList.toggle('hidden');
  });

  // Mobile course dropdown
  const mobileCourseBtn = document.getElementById('mobile-course-btn');
  const mobileCourseMenu = document.getElementById('mobile-course-menu');
  const mobileCourseIcon = document.getElementById('mobile-course-icon');

  mobileCourseBtn.addEventListener('click', () => {
    mobileCourseMenu.classList.toggle('hidden');
    mobileCourseIcon.classList.toggle('fa-chevron-down');
    mobileCourseIcon.classList.toggle('fa-chevron-up');
  });

  // Header scroll effect (smaller on scroll)
  const header = document.getElementById('main-header');
  let lastScrollTop = 0;

  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > 50) {
      header.classList.add('py-2');
      header.classList.remove('py-4');
    } else {
      header.classList.add('py-4');
      header.classList.remove('py-2');
    }

    lastScrollTop = scrollTop;
  });
});
const features = [
  {
    icon: 'fa-book-open',
    title: 'Short, Modular Courses',
    description: 'Learn at your own pace with bite-sized lessons that fit your schedule. Perfect for busy professionals.',
    delay: 100,
  },
  {
    icon: 'fa-robot',
    title: 'AI-Powered Learning',
    description: 'Get personalized quizzes, feedback, and course recommendations based on your progress and goals.',
    delay: 200,
  },
  {
    icon: 'fa-certificate',
    title: 'Verifiable Certificates',
    description: 'Earn industry-recognized certificates that showcase your skills to employers and boost your resume.',
    delay: 300,
  },
];

const container = document.getElementById('features-container');

for (const feature of features) {
  const card = document.createElement('div');
  card.className =
    'bg-white p-6 rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl hover:-translate-y-2';
  card.setAttribute('data-aos', 'fade-up');
  card.setAttribute('data-aos-delay', feature.delay);

  card.innerHTML = `
      <div class="inline-flex items-center justify-center h-16 w-16 rounded-full primary-light-bg mb-4 primary">
        <i class="fas ${feature.icon} text-2xl"></i>
      </div>
      <h3 class="text-xl font-bold mb-2">${feature.title}</h3>
      <p class="text-gray-600">${feature.description}</p>
    `;

  container.appendChild(card);
}



const faqs = [
  {
    question: 'What is SkillUp?',
    answer:
      'SkillUp is an online learning platform that offers short, modular courses with certificates. Our platform features AI-powered learning, video calls, and real-time messaging to enhance your learning experience.',
  },
  {
    question: 'How much does SkillUp cost?',
    answer:
      'Basic access to SkillUp is free, but premium courses and features require a subscription starting at $19/month or $199/year.',
  },
  {
    question: 'Are the certificates recognized?',
    answer:
      'Yes, SkillUp certificates are recognized by many employers. Each certificate includes a verification link that employers can use to confirm its authenticity.',
  },
  {
    question: 'How do the AI features work?',
    answer:
      'Our AI system generates quizzes based on course content, provides personalized feedback on your performance, and recommends courses based on your learning history and goals.',
  },
];

const faqContainer = document.getElementById('faq-container');

for (const faq of faqs) {
  const wrapper = document.createElement('div');
  wrapper.className = 'border-b border-gray-200 pb-4';

  const questionId = `faq-${Math.random().toString(36).substr(2, 9)}`; // Unique ID

  wrapper.innerHTML = `
      <button class="flex items-center justify-between w-full text-left" data-toggle="${questionId}">
        <h3 class="text-lg font-medium">${faq.question}</h3>
        <span class="primary plus-icon"><i class="fas fa-plus"></i></span>
        <span class="primary minus-icon hidden"><i class="fas fa-minus"></i></span>
      </button>
      <div class="mt-3 hidden answer" id="${questionId}">
        <p class="text-gray-600">${faq.answer}</p>
      </div>
    `;

  faqContainer.appendChild(wrapper);
}


faqContainer.addEventListener('click', (e) => {
  const toggleBtn = e.target.closest('button[data-toggle]');
  if (!toggleBtn) return;

  const answerId = toggleBtn.getAttribute('data-toggle');
  const answerEl = document.getElementById(answerId);
  const plusIcon = toggleBtn.querySelector('.plus-icon');
  const minusIcon = toggleBtn.querySelector('.minus-icon');

  const isOpen = !answerEl.classList.contains('hidden');

  answerEl.classList.toggle('hidden');
  plusIcon.classList.toggle('hidden', !isOpen);
  minusIcon.classList.toggle('hidden', isOpen);
});



// Enhanced sidebar toggle functionality
document.getElementById('sidebar-toggle').addEventListener('click', function() {
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.querySelector('.flex-1');
  
  if (sidebar.classList.contains('w-64')) {
      // Collapse sidebar
      sidebar.classList.remove('w-64');
      sidebar.classList.add('w-20');
      mainContent.classList.remove('ml-64');
      mainContent.classList.add('ml-20');
      
      // Hide text in sidebar links with animation
      const sidebarTexts = document.querySelectorAll('#sidebar nav a span');
      sidebarTexts.forEach(text => {
          text.style.opacity = '0';
          setTimeout(() => {
              text.classList.add('hidden');
          }, 300);
      });
      
      // Hide sidebar section titles with animation
      const sidebarTitles = document.querySelectorAll('#sidebar nav div.uppercase');
      sidebarTitles.forEach(title => {
          title.style.opacity = '0';
          setTimeout(() => {
              title.classList.add('hidden');
          }, 300);
      });
      
      // Center icons in sidebar
      const sidebarIcons = document.querySelectorAll('#sidebar nav a svg');
      sidebarIcons.forEach(icon => {
          icon.classList.remove('mr-3');
          icon.parentElement.classList.add('justify-center');
      });
      
      // Store sidebar state in localStorage
      localStorage.setItem('sidebarCollapsed', 'true');
  } else {
      // Expand sidebar
      sidebar.classList.remove('w-20');
      sidebar.classList.add('w-64');
      mainContent.classList.remove('ml-20');
      mainContent.classList.add('ml-64');
      
      // Show text in sidebar links with animation
      const sidebarTexts = document.querySelectorAll('#sidebar nav a span');
      sidebarTexts.forEach(text => {
          text.classList.remove('hidden');
          setTimeout(() => {
              text.style.opacity = '1';
          }, 50);
      });
      
      // Show sidebar section titles with animation
      const sidebarTitles = document.querySelectorAll('#sidebar nav div.uppercase');
      sidebarTitles.forEach(title => {
          title.classList.remove('hidden');
          setTimeout(() => {
              title.style.opacity = '1';
          }, 50);
      });
      
      // Restore icon margin
      const sidebarIcons = document.querySelectorAll('#sidebar nav a svg');
      sidebarIcons.forEach(icon => {
          icon.classList.add('mr-3');
          icon.parentElement.classList.remove('justify-center');
      });
      
      // Store sidebar state in localStorage
      localStorage.setItem('sidebarCollapsed', 'false');
  }
});

// Enhanced user menu toggle with animation
document.getElementById('user-menu-button').addEventListener('click', function(e) {
  e.stopPropagation();
  const userMenu = document.getElementById('user-menu');
  
  if (userMenu.classList.contains('hidden')) {
      // Show menu with animation
      userMenu.classList.remove('hidden');
      userMenu.classList.add('visible');
  } else {
      // Hide menu with animation
      userMenu.classList.remove('visible');
      setTimeout(() => {
          userMenu.classList.add('hidden');
      }, 200);
  }
});

// Close user menu when clicking outside
document.addEventListener('click', function(event) {
  const userMenu = document.getElementById('user-menu');
  const userMenuButton = document.getElementById('user-menu-button');
  
  if (!userMenuButton.contains(event.target) && !userMenu.contains(event.target) && !userMenu.classList.contains('hidden')) {
      userMenu.classList.remove('visible');
      setTimeout(() => {
          userMenu.classList.add('hidden');
      }, 200);
  }
});

// Restore sidebar state from localStorage on page load
document.addEventListener('DOMContentLoaded', ()=> {
  const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
  
  if (sidebarCollapsed) {
      const sidebar = document.getElementById('sidebar');
      const mainContent = document.querySelector('.flex-1');
      
      // Collapse sidebar
      sidebar.classList.remove('w-64');
      sidebar.classList.add('w-20');
      mainContent.classList.remove('ml-64');
      mainContent.classList.add('ml-20');
      
      // Hide text in sidebar links
      const sidebarTexts = document.querySelectorAll('#sidebar nav a span');
      sidebarTexts.forEach(text => {
          text.classList.add('hidden');
          text.style.opacity = '0';
      });
      
      // Hide sidebar section titles
      const sidebarTitles = document.querySelectorAll('#sidebar nav div.uppercase');
      sidebarTitles.forEach(title => {
          title.classList.add('hidden');
          title.style.opacity = '0';
      });
      
      // Center icons in sidebar
      const sidebarIcons = document.querySelectorAll('#sidebar nav a svg');
      sidebarIcons.forEach(icon => {
          icon.classList.remove('mr-3');
          icon.parentElement.classList.add('justify-center');
      });
  }
  
  // Add hover effect to sidebar items
  const sidebarItems = document.querySelectorAll('#sidebar nav a');
  sidebarItems.forEach(item => {
      item.addEventListener('mouseenter', function() {
          if (!this.classList.contains('sidebar-active')) {
              this.classList.add('hover-effect');
          }
      });
      
      item.addEventListener('mouseleave', function() {
          this.classList.remove('hover-effect');
      });
  });
  
  // Add ripple effect to buttons
  const buttons = document.querySelectorAll('button, .btn');
  buttons.forEach(button => {
      button.addEventListener('click', function(e) {
          const x = e.clientX - e.target.getBoundingClientRect().left;
          const y = e.clientY - e.target.getBoundingClientRect().top;
          
          const ripple = document.createElement('span');
          ripple.classList.add('ripple-effect');
          ripple.style.left = `${x}px`;
          ripple.style.top = `${y}px`;
          
          this.appendChild(ripple);
          
          setTimeout(() => {
              ripple.remove();
          }, 600);
      });
  });
});