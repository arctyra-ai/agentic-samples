# Business Plan Generator — Installation Guide

---

## What This App Does

The Business Plan Generator is a local web application that uses artificial intelligence to create comprehensive, professional business plans. You provide basic information about your business—such as your company name, industry, services, and revenue goals—and the app runs an eight-stage AI pipeline that researches your market, develops your service portfolio, writes a full business plan, and then reviews and polishes the final document.

The app runs entirely on your computer. It connects to an AI provider of your choice (such as OpenAI's GPT or Anthropic's Claude) using an API key that you supply. Your API key and business information are never stored on any server—they stay in your browser session. When you are finished, you can download your business plan as a Microsoft Word (.docx) or Markdown (.md) file.

---

## Prerequisites

You need two pieces of software installed on your computer before you begin:

| Software | Minimum Version | How to Check | Download Link |
|----------|----------------|--------------|---------------|
| Node.js  | 18.17.0 or later | Open a terminal and type `node --version` | [https://nodejs.org](https://nodejs.org) — download the **LTS** version |
| npm      | 9.0.0 or later (ships with Node.js) | Open a terminal and type `npm --version` | Installed automatically with Node.js |

> **What is a terminal?**
> - **macOS:** Open the app called **Terminal** (search for it in Spotlight with ⌘+Space).
> - **Windows:** Open **PowerShell** (search for it in the Start menu) or use WSL2 (see below).
> - **Linux:** Open your distribution's terminal application.

If `node --version` prints a number like `v20.14.0`, you are ready. If it prints "command not found" or a version below 18.17.0, install or update Node.js from the link above.

---

## Installation

### macOS

1. **Open Terminal.**

2. **Navigate to where you want the project to live.** For example, to put it on your Desktop:

   ```bash
   cd ~/Desktop
   ```

3. **Download or copy the project folder.** If you received the project as a zip file, unzip it and move the resulting folder to your Desktop (or wherever you chose). Then enter it:

   ```bash
   cd business-plan-generator
   ```

   If the project is in a Git repository:

   ```bash
   git clone <repository-url>
   cd business-plan-generator
   ```

4. **Install dependencies.** This downloads all the libraries the app needs. It may take 1–3 minutes depending on your internet speed:

   ```bash
   npm install
   ```

   You will see progress output. Wait until you see a line that says something like `added XXX packages`. Warnings (yellow text) are normal and can be ignored.

5. **Start the app:**

   ```bash
   npm run dev
   ```

6. **Open your browser** and go to:

   ```
   http://localhost:3000
   ```

   You should see the Business Plan Generator setup screen.

---

### Windows (via WSL2)

The recommended way to run this app on Windows is through WSL2 (Windows Subsystem for Linux), which gives you a Linux terminal inside Windows.

#### Step A: Install WSL2 (skip if you already have it)

1. Open **PowerShell as Administrator** (right-click PowerShell in the Start menu → "Run as administrator").

2. Run:

   ```powershell
   wsl --install
   ```

3. Restart your computer when prompted.

4. After restarting, a Ubuntu terminal window will open and ask you to create a username and password. Choose anything you like—this is just for your local Linux environment.

#### Step B: Install Node.js inside WSL2

1. Open your **Ubuntu** terminal (search for "Ubuntu" in the Start menu).

2. Update the package manager:

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. Install Node.js using the NodeSource repository:

   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

4. Verify the installation:

   ```bash
   node --version
   npm --version
   ```

   Both commands should print version numbers.

#### Step C: Install and run the app

1. Navigate to a convenient location. Your Windows files are accessible under `/mnt/c/`. For example, if the project folder is on your Windows Desktop:

   ```bash
   cd /mnt/c/Users/YOUR_USERNAME/Desktop/business-plan-generator
   ```

   Replace `YOUR_USERNAME` with your actual Windows username.

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the app:

   ```bash
   npm run dev
   ```

4. Open your **Windows browser** (Chrome, Edge, Firefox) and go to:

   ```
   http://localhost:3000
   ```

---

#### Windows Alternative: Without WSL2

If you prefer not to use WSL2, you can run the app directly in PowerShell:

1. Install Node.js from [https://nodejs.org](https://nodejs.org) (download the Windows LTS installer).

2. Open **PowerShell** (regular, not Administrator).

3. Navigate to the project folder:

   ```powershell
   cd C:\Users\YOUR_USERNAME\Desktop\business-plan-generator
   ```

4. Install dependencies:

   ```powershell
   npm install
   ```

5. Start the app:

   ```powershell
   npm run dev
   ```

6. Open your browser to `http://localhost:3000`.

---

### Linux (Ubuntu/Debian)

1. **Open your terminal.**

2. **Install Node.js** if you haven't already:

   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

   For other distributions (Fedora, Arch, etc.), use your package manager or download from [https://nodejs.org](https://nodejs.org).

3. **Verify:**

   ```bash
   node --version
   npm --version
   ```

4. **Navigate to the project folder:**

   ```bash
   cd /path/to/business-plan-generator
   ```

5. **Install dependencies:**

   ```bash
   npm install
   ```

6. **Start the app:**

   ```bash
   npm run dev
   ```

7. **Open your browser** to:

   ```
   http://localhost:3000
   ```

---

## Starting the App

Every time you want to use the app, open a terminal, navigate to the project folder, and run:

```bash
npm run dev
```

You should see output similar to:

```
  ▲ Next.js 14.2.x
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Ready in 2.1s
```

Open `http://localhost:3000` in your web browser. The app is now running.

---

## Stopping the App

In the terminal where the app is running, press:

```
Ctrl + C
```

This stops the development server. You can close the terminal window after that.

---

## Getting an API Key

The app needs an API key from an AI provider to generate your business plan. You only need **one** key from **one** provider. Choose whichever provider you prefer.

### Anthropic (Claude)

1. Go to [https://console.anthropic.com](https://console.anthropic.com).
2. Create an account or sign in.
3. Navigate to **API Keys** (in the left sidebar or under account settings).
4. Click **Create Key**. Give it any name (e.g., "Business Plan Generator").
5. Copy the key. It starts with `sk-ant-...`.
6. Paste it into the app's API Key field on the setup screen.

**Cost note:** Anthropic charges per token (roughly per word) of input and output. A full business plan typically costs between $0.05 and $2.00 depending on the model you choose. Claude 3 Haiku is the cheapest; Claude 3.5 Sonnet produces higher quality at moderate cost. You will need to add credit to your Anthropic account before use.

### OpenAI (GPT)

1. Go to [https://platform.openai.com](https://platform.openai.com).
2. Create an account or sign in.
3. Navigate to **API Keys** (click your profile icon → "API keys", or go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)).
4. Click **Create new secret key**. Give it any name.
5. Copy the key. It starts with `sk-...`.
6. Paste it into the app's API Key field on the setup screen.

**Cost note:** OpenAI charges per token. A full business plan typically costs between $0.05 and $3.00 depending on the model. GPT-4o Mini is the cheapest; GPT-4o produces higher quality. You will need to add credit to your OpenAI account before use.

### Google AI (Gemini)

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **Create API Key**.
4. Copy the key.
5. Paste it into the app's API Key field on the setup screen.

**Cost note:** Google offers a free tier for Gemini API with rate limits. Paid usage is very affordable—a full business plan typically costs under $0.10 with Gemini 1.5 Flash.

### OpenRouter

1. Go to [https://openrouter.ai](https://openrouter.ai).
2. Create an account.
3. Navigate to **Keys** in your dashboard.
4. Create a new key and copy it.
5. In the app, select "OpenRouter" as your provider, then enter the key.

OpenRouter provides access to many models from multiple providers through a single API key.

### Custom Providers

If you are running a local LLM (such as Ollama, LM Studio, or vLLM) or connecting to another OpenAI-compatible API endpoint:

1. Select "Custom Endpoint" as the provider.
2. Enter the full URL of your API endpoint (e.g., `http://localhost:11434/v1/chat/completions` for Ollama with OpenAI compatibility).
3. Enter the model name your endpoint expects.
4. Enter any API key the endpoint requires (or a placeholder if none is needed).

The endpoint must be compatible with the OpenAI chat completions API format.

---

## Troubleshooting

### "Port 3000 is already in use"

Another application is using port 3000. Either:

- Stop the other application, then try again.
- Or start the app on a different port:

  ```bash
  npx next dev -p 3001
  ```

  Then open `http://localhost:3001` instead.

### "node: command not found" or Node version too old

- Install or update Node.js from [https://nodejs.org](https://nodejs.org) (choose the LTS version).
- After installing, **close and reopen your terminal** before trying again.

### "npm install" fails with permission errors

- On macOS/Linux, do **not** use `sudo npm install`. Instead, fix npm permissions:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix '~/.npm-global'
  echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
  source ~/.bashrc
  ```

- On Windows, run PowerShell as Administrator for the install step, or use the Node.js installer which sets permissions correctly.

### "Invalid API key" error

- Double-check that you copied the entire key with no extra spaces.
- Make sure you have billing/credit set up on your AI provider account. Many providers require prepaid credit even for pay-as-you-go plans.
- Ensure you selected the correct provider in the app's dropdown (e.g., don't paste an OpenAI key while "Anthropic" is selected).

### API key validation times out

- Check your internet connection.
- If you are behind a corporate firewall or VPN, ensure that outbound HTTPS connections to your AI provider (e.g., `api.openai.com`) are allowed.

### DOCX download does not work

- Make sure your browser allows downloads from `localhost`.
- Try a different browser.
- Check your browser's download folder—the file may have downloaded but your browser did not show a notification.

### The page is blank or shows an error

- In the terminal where the app is running, look for error messages in red.
- Try stopping the app (`Ctrl+C`) and restarting it (`npm run dev`).
- If you see TypeScript or compilation errors, try deleting the build cache and reinstalling:

  ```bash
  rm -rf .next node_modules
  npm install
  npm run dev
  ```

---

## Data & Privacy

- **Your API key is never saved to disk.** It exists only in your browser's memory while the app is running. When you close the browser tab or refresh the page, it is gone.
- **All your business information stays on your computer.** It is held in browser memory and is never sent to any server except as part of prompts to your chosen AI provider.
- **The only outbound network requests** go from this app to the AI provider you selected (e.g., `api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`, or your custom endpoint). No analytics, telemetry, or tracking of any kind is included.
- **No server-side storage.** The app's backend (the Next.js API routes) processes requests in memory and does not write anything to disk, a database, or any external service.

---

## Updating

If you received the project via Git:

```bash
cd business-plan-generator
git pull origin main
npm install
npm run dev
```

The `npm install` step ensures any new dependencies are downloaded.

If you received the project as a zip file, replace the entire project folder with the new version and run `npm install` again.
