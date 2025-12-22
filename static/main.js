function showPage(pageId) {
            // Скрываем все секции
            document.querySelectorAll('.page').forEach(section => {
                section.classList.remove('active');
            });
            // Показываем нужную
            document.getElementById(pageId).classList.add('active');

            // Скрываем навигацию на странице входа
            const nav = document.getElementById('navbar');
            if(pageId === 'auth') {
                nav.style.display = 'none';
            } else {
                nav.style.display = 'flex';
            }
        }
showPage('auth-view');