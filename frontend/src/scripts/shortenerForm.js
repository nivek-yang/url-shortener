export function shortenerForm() {
  return {
    original_url: '',
    short_url: '',
    password: '',
    notes: '',
    is_active: true,
    isLoading: false,
    errorMessage: '',

    async submit() {
      this.isLoading = true;
      this.errorMessage = '';
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
          if (this.$refs.result) {
            this.$refs.result.innerHTML = `
              <div class="alert alert-success mt-4">
                ${data.message || '短網址建立成功'}:
                <a href="${data.short_url}" target="_blank" class="link link-primary">${data.short_url}</a>
              </div>
            `;
          }
          this.original_url = '';
          this.short_url = '';
          this.password = '';
          this.notes = '';
          this.is_active = true;
        } else {
          this.errorMessage = data.message;
        }
      } catch (error) {
        this.errorMessage = error.message;
      } finally {
        this.isLoading = false;
      }
    },
  };
}
