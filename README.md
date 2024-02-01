# Telegram Bot

This is a Telegram bot designed to handle cleaning checklists for various locations and generate reports based on the completed checklists. The bot allows users to select a location, go through a checklist of items to be cleaned, leave comments if necessary, and upload photos as evidence. Once all checklist items are completed, the bot generates a report and sends it to OpenAI for analysis, providing users with analyzed feedback.

## Features

- **Location Selection**: Users can choose from multiple locations to perform a cleaning checklist.
- **Checklist Handling**: The bot presents a checklist of items to be cleaned for each selected location.
- **Commenting**: Users can leave comments for specific checklist items if needed.
- **Photo Upload**: Users can upload photos as evidence after completing checklist items.
- **Report Generation**: Once all checklist items are completed, the bot generates a report summarizing the cleaning status for each location.
- **OpenAI Integration**: The generated report is sent to OpenAI for analysis, providing users with analyzed feedback.


## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/evgenijmartynuk07/telegram_bot.git
    ```

2. create virtual & Install dependencies:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. Create a `.env` file and add your Telegram Bot token:

    ```env
    TELEGRAM_TOKEN=<your_telegram_token>
    OPENAI_KEY=<your_openAI_key>
    ```

4. Run the bot:

    ```bash
    python bot.py
    ```

## Usage

1. Start the bot by sending the `/start` command.
2. Choose a location from the provided options.
3. Go through the checklist items and mark them as completed or leave comments if necessary.
4. Upload photos as evidence for completed items.
5. Once all checklist items are completed, the bot will generate a report.
6. Analyzed feedback will be provided based on the generated report.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

