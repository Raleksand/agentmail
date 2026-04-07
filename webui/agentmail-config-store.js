import { createStore } from "/js/AlpineStore.js";

export const store = createStore("agentmailConfig", {
  _loaded: false,

  init() {
    if (this._loaded) return;
    if (!window.config) {
      window.config = {};
    }
    if (typeof config.api_base_url !== "string") {
      config.api_base_url = "https://api.agentmail.to/v0";
    }
    if (typeof config.api_key !== "string") {
      config.api_key = "";
    }
    if (typeof config.default_inbox !== "string") {
      config.default_inbox = "";
    }
    this._loaded = true;
  },
});
