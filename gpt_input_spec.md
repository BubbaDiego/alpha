# 📘 GPT Input Specification — Modular Portfolio Analysis
**Version:** 1.0  
**Generated:** 2025-05-26 20:08:36  
**Author:** Geno

---

## 🎯 Purpose
This specification defines the modular JSON format for sending portfolio, alert, and analysis context to GPT. It allows structured evaluation of risk, hedging, and performance.

---

## 🧩 Top-Level File: `gpt_response_wrapper.json`
Acts as the main bundle reference.
```json
{
  "type": "gpt_analysis_bundle",
  "version": "1.0",
  "generated": "YYYY-MM-DDTHH:MM:SSZ",
  "meta_file": "gpt_meta_input.json",
  "definitions_file": "gpt_definitions_input.json",
  "alert_thresholds_file": "gpt_alert_thresholds_input.json",
  "module_reference_file": "gpt_module_references.json",
  "current_snapshot_file": "snapshot_<DATE>.json",
  "previous_snapshot_file": "snapshot_<DATE>.json",
  "instructions_for_ai": "Prompt for GPT's use"
}
```
