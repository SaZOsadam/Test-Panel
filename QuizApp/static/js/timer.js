  // Timer logic 
  let timeLeft = 30;  // Time in seconds
  const timerElement = document.getElementById('timer');

  const timerInterval = setInterval(() => {
    timerElement.textContent = `${timeLeft} second`;
    timeLeft -= 1;

    if (timeLeft < 0) {
      clearInterval(timerInterval);
      // Automatically submit the form
      document.getElementById('quiz-form').submit();
    }
  }, 1000);

