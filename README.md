# LLaMA 2 Chatbot App

This is an experimental Streamlit chatbot app built for LLaMA2 (or any other LLM). The app includes session chat history and provides an option to select multiple LLaMA2 API endpoints on Replicate. 

You can test the LLaMA 7B & 13B chat models and this app in www.LLaMA2.ai

## Features

- Chat history is maintained for each session (if you refresh, chat history clears)
- Option to select between different LLaMA2 chat API endpoints (7B or 13B). Default is 13B.
- Configure model hyperparameters from the sidebar (Temperature, Top P, Max Sequence Length).
- Includes "User:" and "Assistant:" prompts for the chat conversation.
- Each model (7B & 13B) runs on Replicate - (One A100 (40Gb)).
- Docker image included to deploy this app in Fly.io

## Installation

- Clone the repository
- Install dependencies with `pip install -r requirements.txt`
- Copy the '.env_template' file to '.env' and add your Replicate API key
    - For your convenience, we intentionally include model endpoints in the '.env_template' file
- Run the app with `streamlit run llama2_chatbot.py`
- Docker image included to [deploy this app](#deploying-on-flyio) in Fly.io

## Usage

- Start the chatbot by selecting an API endpoint from the sidebar.
- Configure model hyperparameters from the sidebar.
- Type your question in the input field at the bottom of the app and press enter.

## Deploying on fly.io
1. First you should [install flyctl](https://fly.io/docs/hands-on/install-flyctl/) and login from command line
2. `fly launch` -> this will generate a fly.toml for you automatically
3. `fly deploy --dockerfile Dockerfile` --> this will automatically package up the repo and deploy it on fly. If you have a free account, you can use `--ha=false` flag to only spin up one instance
4. Go to your deployed fly app dashboard, click on `Secrets` from the left hand side nav, and click on `Use the Web CLI to manage your secrets without leaving your browser`. Once you are on your app's web CLI, export all secrets needed. i.e `export REPLICATE_API_TOKEN=your_replicate_token`. Refer to .env.example file for necessary secrets. 

## Authors

- Marco Mascorro - [@mascobot](https://twitter.com/Mascobot)
- Yoko Li - [@stuffyokodraws](https://twitter.com/stuffyokodraws)
- Rajko Radovanović - [@rajko_rad](https://twitter.com/rajko_rad)
- Matt Bornstein - [@BornsteinMatt](https://twitter.com/BornsteinMatt)
- Guido Appenzeller - [@appenz](https://twitter.com/appenz)

## Version

0.9.0 (Experimental) - July 2023

## Contributing

This project is under development. Contributions are welcome!

## License

- Web chatbot license (this repo): Apache 2.0
- For the LLaMA models license, please refer to the License Agreement from Meta Platforms, Inc.

## Acknowledgements

- Special thanks to the team at Meta AI, Replicate, a16z-infra and the entire open-source community.

## Disclaimer

This is an experimental version of the app. Use at your own risk. While the app has been tested, the authors hold no liability for any kind of losses arising out of using this application. 

## UI Configuration

The app has been styled and configured for a cleaner look. Main menu and footer visibility have been hidden. Feel free to modify this to your custom application.

## Resources

- [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
- [GitHub to deploy LLaMA2 on Replicate](https://github.com/a16z-infra/cog-llama-template)
