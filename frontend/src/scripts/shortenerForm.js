export function shortenerForm() {
  return {
    original_url: '',
    short_url: '',
    password: '',
    notes: '',
    is_active: true,
    isLoading: false,
    isFetchingInfo: false,
    message: '',
    messageType: '',
    short_url_result: '',

    async submit() {
      this.isLoading = true;
      this.message = '';
      if (this.$refs.result) this.$refs.result.innerHTML = '';

      const payload = {
        original_url: this.original_url,
        slug: this.short_url || undefined,
        password: this.password || undefined,
        notes: this.notes || undefined,
        is_active: this.is_active,
      };

      try {
        const res = await fetch('/api/links/shortener', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.message || '發生未知錯誤');
        }

        if (data.success) {
          this.message = data.message;
          this.messageType = 'success';
          this.short_url_result = data.short_url;

          this.original_url = '';
          this.short_url = '';
          this.password = '';
          this.notes = '';
          this.is_active = true;
        } else {
          this.message = data.message;
          this.messageType = 'error';
          this.short_url_result = '';
        }
      } catch (error) {
        this.message = error.message;
        this.messageType = 'error';
      } finally {
        this.isLoading = false;
      }
    },

    async fetchPageInfo() {
      if (!this.original_url) {
        alert('請先輸入或貼上完整的網址！');
        return;
      }

      this.isFetchingInfo = true;
      this.message = ''; // 清除舊的錯誤訊息

      try {
        const res = await fetch('/api/fetch-page-info/', {
          // <-- 指向新的 API
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ original_url: this.original_url }),
        });

        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.message || '抓取資訊失敗');
        }

        // 成功時，將回傳的 notes 文字更新到 Alpine 的狀態中
        // 因為 textarea 綁定了 x-model="notes"，所以會自動更新
        this.notes = data.notes;
      } catch (error) {
        this.message = error.message;
      } finally {
        this.isFetchingInfo = false;
      }
    },

    copyToClipboard(text) {
      navigator.clipboard
        .writeText(text)
        .then(() => {
          alert('已複製短網址！');
          // 如果有需要，可以在這裡更新 UI 或做其他處理
        })
        .catch(() => {
          alert('複製失敗');
        });
    },
  };
}
