export function indexShortener() {
  return {
    original_url: '',
    isLoading: false,
    result: null,

    async submit() {
      if (!this.original_url) return;
      this.isLoading = true;
      this.result = null;
      try {
        const res = await fetch('/api/links/shortener', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ original_url: this.original_url }),
        });
        const data = await res.json();
        this.result = {
          success: res.ok,
          message: data.message,
          short_url: data.short_url || null,
        };
      } catch (error) {
        this.result = {
          success: false,
          message: '網路連線錯誤，請稍後再試。',
          short_url: null,
        };
      } finally {
        this.isLoading = false;
      }
    },
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        // 你可以換成更漂亮的提示，例如使用 DaisyUI 的 toast
        alert('已成功複製到剪貼簿！');
      });
    },
  };
}
