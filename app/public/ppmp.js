document.querySelectorAll('.line-form').forEach(form => {
  const money = cents => '₱' + (Number(cents) / 100).toLocaleString('en-PH', {minimumFractionDigits: 2, maximumFractionDigits: 2});
  form.addEventListener('input', () => {
    let total = 0n;
    form.querySelectorAll('[data-quarter]').forEach(input => {
      const output = form.querySelector(`[data-amount="${input.dataset.quarter}"]`);
      if (!/^\d{1,5}(\.\d{1,3})?$/.test(input.value)) { output.textContent = '—'; return; }
      const parts = input.value.split('.');
      const milli = BigInt(parts[0]) * 1000n + BigInt((parts[1] || '').padEnd(3, '0'));
      const cents = (milli * BigInt(form.dataset.cost) + 500n) / 1000n;
      total += cents; output.textContent = money(cents);
    });
    form.querySelector('[data-total]').textContent = money(total);
    form.querySelector('[data-save-state]').textContent = 'Preview · Unsaved changes';
    form.dataset.dirty = 'true';
  });
  form.addEventListener('submit', () => { delete form.dataset.dirty; });
});
window.addEventListener('beforeunload', event => {
  if (document.querySelector('.line-form[data-dirty="true"]')) { event.preventDefault(); event.returnValue = ''; }
});
document.querySelectorAll('.remove-form').forEach(form => form.addEventListener('submit', event => {
  if (!confirm('Remove this item from your draft?')) event.preventDefault();
}));
