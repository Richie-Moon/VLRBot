import discord
from discord import app_commands, ui
import requests
import json


guild = discord.Object(id=716770439862681620)


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=guild)
            self.synced = True
        print(f"Logged in as {self.user}")


class Questionnaire(ui.Modal, title="Questionnaire"):
    name = ui.TextInput(label='Name')
    answer = ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your response,'
                                                f' {self.name}!',
                                                ephemeral=True)


class Matches(ui.Select):
    def __init__(self):
        tournaments = []

        super().__init__(placeholder='Select Match')


class Tournaments(ui.Select):
    def __init__(self):
        self.get = requests.get('https://vlrggapi.vercel.app/match/results').text
        self.data = json.loads(self.get)

        count = 0
        tournament_names = []
        tournaments = []
        for match in self.data['data']['segments']:
            if count != 25:
                option = match['tournament_name']
                if option in tournament_names:
                    pass
                else:
                    tournament_names.append(option)
                    count += 1
            else:
                break

        for tournament in tournament_names:
            tournaments.append(discord.SelectOption(label=tournament))

        super().__init__(placeholder="Select Tournament", options=tournaments)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=MatchView())


class TournamentView(ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Tournaments())


class MatchView(ui.view):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Matches())


client = aclient()
tree = app_commands.CommandTree(client)


@tree.command(guild=guild)
async def test(interaction: discord.Interaction, number: int, string: str):
    await interaction.response.send_message(f'{number=} {string=}',
                                            ephemeral=False)


@tree.command(guild=guild)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f'{round(client.latency * 1000)}ms')


@tree.command(guild=guild)
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(Questionnaire())


@tree.command(guild=guild)
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(view=TournamentView())


client.run(
    'MTAxNTIzNzAxMTgzNTE5MTM4Ng.GlheMq.3JPuH0tsFuNnwVNy37TPEIBI_Jyg48BscWz2Sg')
