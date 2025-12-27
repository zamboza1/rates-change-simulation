# 05_SECURITY_CHECKLIST.md

## Security Checklist

### Network & Data
- [ ] Requests use timeouts (default 10s)
- [ ] Inputs for year/month are validated (no arbitrary URL injection)
- [ ] Cache path is fixed under `data/cache` (no user-controlled file paths)
- [ ] `.env` not committed to version control

### Code Safety
- [ ] No `eval()` or dangerous deserialization.
- [ ] XML parsing uses standard, safe libraries (e.g., `xml.etree.ElementTree`).
- [ ] Error messages do not leak internal paths or stack traces to end users.
