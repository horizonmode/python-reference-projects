import {LitElement, html, css} from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

// Django supplies the content; Lit supplies the reusable card presentation.
export class WeatherCard extends LitElement {

  static styles = css`
    :host {
      display: block;
      margin-top: 1.5rem;
    }

    .card {
      padding: 1.5rem;
      border: 1px solid #cbd5e1;
      border-radius: 1rem;
      background: #f8fafc;
      color: #0f172a;
      box-shadow: 0 4px 12px rgb(15 23 42 / 6%);
    }

    ::slotted(h2) {
      margin-top: 0;
    }
  `;

  render() {
    return html`
      <div class="card">
        <slot></slot>
      </div>
    `;
  }
}

customElements.define('weather-card', WeatherCard);

