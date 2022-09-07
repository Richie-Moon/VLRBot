import discord
from discord import app_commands, ui
import requests
import json
from os import environ
from dotenv import load_dotenv
import datetime


def convert_to_unix(time_data: str):
    dt_now = datetime.datetime.now()
    time_data = time_data.split()

    if len(time_data) == 3:
        time_data.pop(-1)
        for item in time_data:
            if item[1] == 'w':
                dt_now -= datetime.timedelta(weeks=float(item[0]))
            elif item[1] == 'd':
                dt_now -= datetime.timedelta(days=float(item[0]))
            elif item[1] == 'h':
                dt_now -= datetime.timedelta(hours=float(item[0]))
            elif item[1] == 'm':
                dt_now -= datetime.timedelta(minutes=float(item[0]))
            elif item[1] == 's':
                dt_now -= datetime.timedelta(seconds=float(item[0]))

    elif len(time_data) == 4:
        for i in range(2):
            time_data.pop(-1)

        for item in time_data:
            if item[1] == 'w':
                dt_now += datetime.timedelta(weeks=float(item[0]))
            elif item[1] == 'd':
                dt_now += datetime.timedelta(days=float(item[0]))
            elif item[1] == 'h':
                dt_now += datetime.timedelta(hours=float(item[0]))
            elif item[1] == 'm':
                dt_now += datetime.timedelta(minutes=float(item[0])+1)
            elif item[1] == 's':
                dt_now += datetime.timedelta(seconds=float(item[0]))

    if 'd' in time_data:
        return int(datetime.datetime.strptime(str(dt_now.date()), '%Y-%m-%d').timestamp())
    else:
        return int(datetime.datetime.timestamp(dt_now))


load_dotenv()
token = environ['TOKEN']

guilds = [discord.Object(id=716770439862681620), discord.Object(id=792309472784547850)]


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=guilds[1])
            self.synced = True
        print(f"Logged in as {self.user}")


client = aclient()
tree = app_commands.CommandTree(client)


# class Questionnaire(ui.Modal, title="Questionnaire"):
#     name = ui.TextInput(label='Name')
#     answer = ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)
#
#     async def on_submit(self, interaction: discord.Interaction):
#         await interaction.response.send_message(f'Thanks for your response,'
#                                                 f' {self.name}!',
#                                                 ephemeral=True)


class Matches(ui.Select):
    """Takes the tournament name as an argument and finds all the matches from that tournament.
    Sends that list to the user in a dropdown menu. """

    def __init__(self, name, url_type):
        self.name = name
        self.url_type = url_type
        if self.url_type == 'results':
            self.get = requests.get('https://vlrggapi.vercel.app/match/results').text
        else:
            self.get = requests.get('https://vlrggapi.vercel.app/match/upcoming').text
        self.data = json.loads(self.get)['data']['segments']

        self.matches = []
        for match in self.data:
            if match['tournament_name'] == self.name:
                self.matches.append(match)

        options = []
        for option in self.matches:
            options.append(discord.SelectOption(label=f"{option['team1']} vs {option['team2']}",
                                                description=option['round_info'],
                                                value=str(self.matches.index(option))))

        super().__init__(placeholder='Select Match', options=options)

    async def callback(self, interaction: discord.Interaction):
        match = self.matches[int(self.values[0])]

        if self.url_type == 'results':
            unix = convert_to_unix(match['time_completed'])
            embed = discord.Embed(color=discord.Color.from_rgb(138, 43, 226),
                                  timestamp=interaction.created_at,
                                  title=f"{match['team1']} vs {match['team2']}")

            if int(match['score1']) > int(match['score2']):
                embed.add_field(name=f"Result:",
                                value=f"**:{match['flag1']}: {match['team1']} {match['score1']}**:"
                                      f"{match['score2']} {match['team2']} :{match['flag2']}:",
                                inline=True)
                embed.add_field(name="Info:", value=f"**Winner:** {match['team1']}"
                                                    f"\n**Round: ** {match['round_info']}"
                                                    f"\n**Time:** <t:{unix}> (<t:{unix}:R>)"
                                                    f"\n**Site:** https://vlr.gg{match['match_page']}",
                                inline=False)
            else:
                embed.add_field(name=f"Result:",
                                value=f":{match['flag1']}: {match['team1']} {match['score1']}:"
                                      f"**{match['score2']} {match['team2']} :{match['flag2']}:**",
                                inline=True)
                embed.add_field(name='Info:', value=f"**Winner:** {match['team2']}"
                                                    f"\n**Round: ** {match['round_info']}"
                                                    f"\n**Time:** <t:{unix}> (<t:{unix}:R>)"
                                                    f"\n**Site:** https://vlr.gg{match['match_page']}"
                                                    f"\n", inline=False)

            embed.set_author(icon_url=match['tournament_icon'], name=match['tournament_name'])
            await interaction.response.send_message(embed=embed)

        else:
            unix = convert_to_unix(match['time_until_match'])
            print(unix)
            embed = discord.Embed(colour=discord.Color.from_rgb(255, 87, 51),
                                  timestamp=interaction.created_at,
                                  title=f"{match['team1']} vs {match['team2']}")
            embed.set_author(icon_url=match['tournament_icon'], name=match['tournament_name'])
            embed.add_field(name="Info:", value=f"\n**Round: ** {match['round_info']}"
                                                f"\n**Time:** <t:{unix}> (<t:{unix}:R>)"
                                                f"\n**Site:** https://vlr.gg{match['match_page']}")
            await interaction.response.send_message(embed=embed)


class Tournaments(ui.Select):
    """Gets a list of recent tournaments and sends all the options in a dropdown menu. """

    def __init__(self, url_type: str):
        self.url_type = url_type
        if self.url_type == 'results':
            self.get = requests.get('https://vlrggapi.vercel.app/match/results').text
        else:
            self.get = requests.get('https://vlrggapi.vercel.app/match/upcoming').text
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
        await interaction.response.send_message(
            view=MatchView(name=self.values[0], url_type=self.url_type))


class TournamentView(ui.View):
    def __init__(self, *, timeout=180, url_type):
        super().__init__(timeout=timeout)
        self.add_item(Tournaments(url_type=url_type))


class MatchView(ui.View):
    def __init__(self, name, *, timeout=180, url_type: str):
        super().__init__(timeout=timeout)
        self.add_item(Matches(name=name, url_type=url_type))


@tree.command(guilds=guilds)
async def test(interaction: discord.Interaction, number: int, string: str):
    await interaction.response.send_message(f'{number=} {string=}',
                                            ephemeral=False)


@tree.command(guilds=guilds)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'{round(client.latency * 1000)}ms')


# @tree.command(guilds=guilds)
# async def modal(interaction: discord.Interaction):
#     await interaction.response.send_modal(Questionnaire())


@tree.command(guilds=guilds)
async def results(interaction: discord.Interaction):
    await interaction.response.send_message(view=TournamentView(url_type='results'))


@results.error
async def results_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message("Data Fetch timed out. ")


@tree.command(guilds=guilds)
async def upcoming(interaction: discord.Interaction):
    await interaction.response.send_message(view=TournamentView(url_type='upcoming'))


@upcoming.error
async def upcoming_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message("Data Fetch timed out")


client.run(token)
