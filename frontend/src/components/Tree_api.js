import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Box, Button, Card, CardContent, Typography, Grid, Paper, ThemeProvider, createTheme, useTheme } from '@mui/material';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const positions = ['BTNvBB', 'COvBTN'];
const flopTextures = ['Dynamic Unpaired', 'Dry Unpaired', 'Straight', 'Paired', 'Monotone'];
const potTypes = ['Single-Raised Pot', '3bet Pot'];

const Tree_api = () => {
  const theme = useTheme();

  const [selectedPosition, setSelectedPosition] = useState(null);
  const [selectedTexture, setSelectedTexture] = useState(null);
  const [selectedPotType, setSelectedPotType] = useState('Single-Raised Pot');
  const [betSizes, setBetSizes] = useState({});
  const [betFrequencies, setBetFrequencies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (selectedPosition && selectedTexture) {
      fetchData();
    }
  }, [selectedPosition, selectedTexture, selectedPotType]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/poker-data/', {
        params: {
          pot_type: selectedPotType,
          position: selectedPosition,
          flop_texture: selectedTexture
        }
      });
      const { bet_sizes, bet_frequencies } = response.data;
      setBetSizes(bet_sizes);
      setBetFrequencies(bet_frequencies);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getPlayerColor = (player) => {
    if (player === 'BB' || player === 'CO') {
      return theme.palette.primary.main;
    } else {
      return theme.palette.secondary.main;
    }
  };

  const handlePositionClick = (position) => {
    setSelectedPosition(position);
    setSelectedTexture(null);
  };

  const handleTextureClick = (texture) => {
    setSelectedTexture(texture);
  };

  const handlePotTypeClick = (potType) => {
    setSelectedPotType(potType);
  };

  const getChartData = () => {
    return betFrequencies;
  };

  const getBarConfig = () => {
    if (betFrequencies.length === 0) return [];
    const players = Object.keys(betFrequencies[0]).filter(key => key !== 'name');
    return players.map(player => ({
      dataKey: player,
      fill: getPlayerColor(player)
    }));
  };

  return (
    <Box sx={{ maxWidth: '4xl', margin: 'auto', p: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Poker Hand Decision Tree
      </Typography>
      
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Pot Type:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {potTypes.map((potType) => (
            <Button
              key={potType}
              variant={selectedPotType === potType ? "contained" : "outlined"}
              color="primary"
              onClick={() => handlePotTypeClick(potType)}
            >
              {potType}
            </Button>
          ))}
        </Box>
        <Typography variant="h6" gutterBottom>
          Position:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {positions.map((position) => (
            <Button
              key={position}
              variant={selectedPosition === position ? "contained" : "outlined"}
              color="primary"
              onClick={() => handlePositionClick(position)}
            >
              {position}
            </Button>
          ))}
        </Box>
          <Typography variant="h6" gutterBottom>
            Flop Texture:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {flopTextures.map((texture) => (
              <Button
                key={texture}
                variant={selectedTexture === texture ? "contained" : "outlined"}
                color="secondary"
                size="small"
                onClick={() => handleTextureClick(texture)}
              >
                {texture}
              </Button>
            ))}
          </Box>
      </Paper>

      {isLoading && <Typography>Loading...</Typography>}
      {error && <Typography color="error">{error}</Typography>}

      {!isLoading && !error && selectedPosition && selectedTexture && (
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Bet Sizes (% of Pot):
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(betSizes).map(([player, size]) => (
                <Grid item xs={6} key={player}>
                  <Paper 
                    elevation={3} 
                    sx={{ 
                      p: 2, 
                      backgroundColor: getPlayerColor(player),
                      color: theme.palette.getContrastText(getPlayerColor(player))
                    }}
                  >
                    <Typography variant="h5" fontWeight="bold">
                      {player}
                    </Typography>
                    <Typography variant="h4">
                      {size}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Bet Frequency:
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={getChartData()}>
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
                  <Tooltip formatter={(value) => `${value}%`} />
                  <Legend />
                  {getBarConfig().map((bar, index) => (
                    <Bar key={index} {...bar} />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Tree_api;