using LightGraphs
using DataFrames
using CSV
using GraphPlot
using Compose
using ColorSchemes
using Colors

using Plots
pyplot()


# TODO: not sure if parametrising type is a good idea
function create_id_nodename_map(node_names::AbstractArray{T}) where T
  id_name_map = Dict{Int64, T}()
  for (i, c) in enumerate(node_names)
      id_name_map[i] = c
  end
  id_name_map
end


function add_edges!(G, node_edge_map, name_id_map; verbose::Bool=false)
  for (x, y) in node_edge_map
    verbose && println("($(name_id_map[x]): $x) → ($(name_id_map[y]): $y)")
    add_edge!(G, name_id_map[x], name_id_map[y])
  end
end


function team_maps(df::DataFrame)
  killer_team_map = Dict(zip(df[:killer], df[:killer_team_id]))
  victim_team_map = Dict(zip(df[:victim], df[:victim_team_id]))
  killer_team_map, victim_team_map
end


get_players(df::DataFrame) = union(df[:killer], df[:victim])


function player_id_maps(df::DataFrame)
  id_player_map = create_id_nodename_map(get_players(df))
  player_id_map = map(reverse, id_player_map)
  id_player_map, player_id_map
end


function build_graph(df::DataFrame)

  node_edge_map = zip(df[:killer], df[:victim])
  id_player_map, player_id_map = player_id_maps(df)

  G = DiGraph(length(id_player_map))
  add_edges!(G, node_edge_map, player_id_map)
  
  G
end

function print_properties(G::AbstractGraph)
  println("is_directed: $(is_directed(G))")
  println("n_vetrices: $(nv(G))")
  println("n_edges: $(ne(G))")
  println("has_self_loops: $(has_self_loops(G))")
end


function player_kill_counts(df)
  players = get_players(df)

  player_kills = Dict{String, Float64}()
  for player in players
    player_kills[player] = 0
  end

  for k in df[:killer]   
    player_kills[k] += 1
  end

  player_kills
end


team_colour_map(n_teams) = get(ColorSchemes.rainbow, collect(linspace(0, 1, n_teams)))


function player_team_colour_map(players, player_team_map, team_colours)

  player_team_colour = Dict()
  for player in players
    team_id = player_team_map[player]
    if team_id == 0
      player_team_colour[player] = RGB{Float64}(128/256, 128/256, 128/256)
    else
      player_team_colour[player] = team_colours[player_team_map[player]]
    end
  end

  player_team_colour
end


function generate_graph_plot(G::AbstractGraph, player_kills, id_player_map, player_team_colour, output::String)

  srand(312132)
  loc_x, loc_y = spring_layout(G)

  node_sizes = [player_kills[id_player_map[i]] + 1 for i in 1:nv(G)]  # add one to offset zero sized nodes
  node_sizes .^= 0.3  # zoom factor

  draw(
    PNG(output, (1920 - 1920 * 0.1)*2px, (1080 - 1080 * 0.1)*2px),
    gplot(
      G, 
      nodelabel=[id_player_map[i] for i in 1:nv(G)],
      nodesize=node_sizes,
      # nodelabelsize=node_sizes,
      nodefillc=[player_team_colour[id_player_map[i]] for i in 1:nv(G)],
      arrowlengthfrac=0.02,
      loc_x, loc_y
    ),
  )

end



function main()
  match_id = "64c6a84d-49b4-4c6c-943e-26bc8676b611"
  filename = "pubg_kill_events_$(match_id).csv"

  path_kill_events = "c:/workspace/pubg-analytics/output/$filename"

  df = CSV.read(path_kill_events)
  println(tail(df))

  killer_team_map, victim_team_map = team_maps(df)
  player_team_map = merge(killer_team_map, victim_team_map)

  players = get_players(df)
  id_player_map, player_id_map = player_id_maps(df)

  G = build_graph(df)
  print_properties(G)

  player_kills = player_kill_counts(df)

  n_teams = maximum(values(player_team_map))  # + 1  # for non-killer caused deaths
  team_colours = team_colour_map(n_teams)
  
  player_team_colour = player_team_colour_map(players, player_team_map, team_colours)


  output_path = "c:/workspace/pubg-analytics/output/pubg_kill_graph_$match_id.png"
  generate_graph_plot(G, player_kills, id_player_map, player_team_colour, output_path)

end


main()


