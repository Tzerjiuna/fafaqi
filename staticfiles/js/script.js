 document.addEventListener('DOMContentLoaded', function() {
        // 为所有footer-title添加点击事件
        const titles = document.querySelectorAll('.footer-title');
        titles.forEach(title => {
            title.addEventListener('click', function() {
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                if (content.style.display === 'block') {
                    content.style.display = 'none';
                } else {
                    content.style.display = 'block';
                }
            });
        });
    });