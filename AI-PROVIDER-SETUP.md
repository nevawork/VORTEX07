# 🤖 Multi-AI Provider System Guide

## Overview

The VORTEXINF bot now supports multiple AI providers! You can choose between:

- **🤖 Groq API** - Fast, real-time responses
- **✨ Google Gemini** - Advanced reasoning and creative responses

## Setup Instructions

### Prerequisites

You need API keys for the providers you want to use:

#### 1. Groq API Key
1. Go to https://console.groq.com
2. Sign up and create an API key
3. Add to your `.env` file:
   ```
   GROQ_API_KEY=your_groq_key_here
   ```

#### 2. Google Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Click "Get API Key"
3. Copy your API key
4. Add to your `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_key_here
   ```

### Full .env Configuration

```env
# Discord Bot
TOKEN=your_bot_token
WEBHOOK_URL=your_webhook_url
BOT_PREFIX=&
OWNER_IDS=your_id

# AI Providers
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

## Using the AI Provider System

### Enable/Disable AI

**Enable AI in a channel:**
```
&ai enable
```
This activates AI responses in the current channel.

**Disable AI:**
```
&ai disable
```
This stops AI responses.

### Select AI Provider

**Switch between providers:**
```
&ai provider
```

You'll see two buttons:
- 🤖 **Groq API** - Click to use Groq
- ✨ **Google Gemini** - Click to use Gemini

### Set Custom Personality

**Customize AI responses:**
```
&ai personality
```

A modal will pop up where you can write custom instructions for how the AI should respond to you.

## Comparison: Groq vs Gemini

| Feature | Groq | Gemini |
|---------|------|--------|
| **Speed** | ⚡ Very Fast | 🟡 Moderate |
| **Reasoning** | Good | Excellent |
| **Creativity** | Good | Very Good |
| **Cost** | Free tier | Free tier |
| **Best For** | Quick responses | Complex tasks |
| **Code** | Good | Excellent |
| **Conversation** | Natural | Very Natural |

## Commands Overview

### AI Management
```
&ai enable              - Enable AI chatbot
&ai disable             - Disable AI chatbot
&ai provider            - Select AI provider (Groq/Gemini)
&ai personality         - Set custom personality
```

### Roleplay Features
```
&ai roleplay-enable     - Enable roleplay mode
&ai roleplay-disable    - Disable roleplay mode
```

## Database

The system uses SQLite to store:
- **chatbot_settings** - Server AI settings and provider selection
- **chatbot_history** - Conversation history
- **conversation_memory** - User preferences and memory
- **user_personalities** - Custom personality prompts

## Troubleshooting

### AI not responding?
1. Check if AI is enabled: `&ai enable`
2. Verify API keys are set in `.env`
3. Check bot logs for errors

### Wrong AI provider selected?
1. Use `&ai provider` to switch
2. The bot will immediately use the new provider

### API key errors?
1. Verify keys are correct in `.env`
2. Make sure you didn't accidentally include quotes
3. Restart the bot after updating `.env`

## Features Enabled

✅ **Multi-Provider Support** - Switch between Groq and Gemini
✅ **Conversation Memory** - AI remembers previous messages
✅ **Custom Personalities** - Set how AI responds to you
✅ **History Tracking** - All conversations are saved
✅ **Automatic Cleanup** - Old conversations cleaned up weekly
✅ **Important Context Preservation** - Key conversations kept longer
✅ **Roleplay Mode** - Interactive character roleplay

## Admin Only

All provider switching requires **Administrator** permissions.

## Future Improvements

Possible future additions:
- OpenAI API support
- Claude API integration
- Local LLM support
- Provider load balancing
- Cost tracking per provider
- Provider-specific settings

## Support

For issues or questions:
1. Join the Discord: https://discord.gg/98qaRWnKuH
2. Contact: @itsfizys
3. Check logs for detailed error messages
