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


# class Questionnaire(ui.Modal, title="Questionnaire"):
#     name = ui.TextInput(label='Name')
#     answer = ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)
#
#     async def on_submit(self, interaction: discord.Interaction):
#         await interaction.response.send_message(f'Thanks for your response,'
#                                                 f' {self.name}!',
#                                                 ephemeral=True)


class Matches(ui.Select):
    """Takes the tournament name as an argument and finds all the matches from that tournament. Sends that list to the
    user in a dropdown menu. """
    def __init__(self, name):
        self.name = name
        self.get = requests.get('https://vlrggapi.vercel.app/match/results').text
        self.data = json.loads(self.get)['data']['segments']

        self.matches = []
        for match in self.data:
            if match['tournament_name'] == self.name:
                self.matches.append(match)

        options = []
        for option in self.matches:
            options.append(discord.SelectOption(label=f"{option['team1']} vs {option['team2']}",
                                                description=option['round_info']))

        super().__init__(placeholder='Select Match', options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.from_rgb(138, 43, 226), timestamp=interaction.created_at,
                              title=self.values[0])
        for match in self.matches:
            print(match['team1'])
            print(self.values[0].split('vs')[0].strip())
            if match['team1'] == self.values[0].split('vs')[0].strip():
                index = self.data.index(match)

        embed.set_author(icon_url=self.data[index]['tournament_icon'], name=self.data[index]['tournament_name'])
        await interaction.response.send_message(embed=embed)


class Tournaments(ui.Select):
    """Gets a list of recent tournaments and sends all the options in a dropdown menu. """
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
        await interaction.response.send_message(view=MatchView(name=self.values[0]))


class TournamentView(ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Tournaments())


class MatchView(ui.View):
    def __init__(self, name, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Matches(name=name))


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


# @tree.command(guild=guild)
# async def modal(interaction: discord.Interaction):
#     await interaction.response.send_modal(Questionnaire())


@tree.command(guild=guild)
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(view=TournamentView())


client.run('MTAxNTIzNzAxMTgzNTE5MTM4Ng.GMydV_.YlOnOjFTMoa62qg6t3yfmA5n7JjgaY9vduLmyY')

# TODO DO NOT PUSH WITH THE TOKEN YOU IDIOT.
