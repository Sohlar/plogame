import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Paper,
  ThemeProvider,
  createTheme,
  useTheme
} from '@mui/material';

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

const betSizes = {
  'Single-Raised Pot': {
    'BTNvBB': {
      'BTN': { 'Dynamic Unpaired': 67, 'Dry Unpaired': 50, 'Straight': 50, 'Paired': 33, 'Monotone': 33 },
      'BB': { 'Dynamic Unpaired': 67, 'Dry Unpaired': 50, 'Straight': 50, 'Paired': 33, 'Monotone': 33 },
    },
    'COvBTN': {
      'CO': { 'Dynamic Unpaired': 60, 'Dry Unpaired': 60, 'Straight': '50-60', 'Paired': 33, 'Monotone': 33 },
      'BTN': { 'Dynamic Unpaired': 60, 'Dry Unpaired': 60, 'Straight': '50-60', 'Paired': 'A33r: 80%   QQ5r: 33%   877ds: 67%', 'Monotone': 33 },
    },
  },
  '3bet Pot': {
    'BTNvBB': {
      'BTN': { 'Dynamic Unpaired': 0, 'Dry Unpaired': 0, 'Straight': 0, 'Paired': 0, 'Monotone': 0 },
      'BB': { 'Dynamic Unpaired': 0, 'Dry Unpaired': 0, 'Straight': 0, 'Paired': 0, 'Monotone': 0 },
    },
    'COvBTN': {
      'CO': { 'Dynamic Unpaired': 0, 'Dry Unpaired': 0, 'Straight': 0, 'Paired': 0, 'Monotone': 0 },
      'BTN': { 'Dynamic Unpaired': 0, 'Dry Unpaired': 0, 'Straight': 0, 'Paired': 0, 'Monotone': 0 },
    },
  },
};

const betFrequencies = {
  'Single-Raised Pot': {
    'BTNvBB': {
      'Dynamic Unpaired': [
        { name: 'A98', BB: 2, BTN: 58 },
        { name: 'QJ7', BB: 5, BTN: 51 },
        { name: 'J85', BB: 13, BTN: 52 },
      ],
      'Dry Unpaired': [
        { name: 'AJ4', BB: 3, BTN: 66 },
        { name: 'Q75', BB: 18, BTN: 54 },
        { name: 'T72', BB: 14, BTN: 57 },
      ],
      'Straight': [
        { name: 'KQJds', BB: 3, BTN: 50 },
        { name: '987r', BB: 26, BTN: 46 },
        { name: '653ds', BB: 19, BTN: 51 },
      ],
      'Paired': [
        { name: 'A33', BB: 4, BTN: 61 },
        { name: 'QQ5', BB: 21, BTN: 74 },
        { name: '877', BB: 15, BTN: 54 },
      ],
      'Monotone': [
        { name: 'A92', BB: 3, BTN: 48 },
        { name: 'KJ8', BB: 4, BTN: 52 },
        { name: 'T54', BB: 9, BTN: 59 },
      ],
    },
    'COvBTN': {
      'Dynamic Unpaired': [
        { name: 'A98', CO: 46, BTN: 41 },
        { name: 'QJ7', CO: 14, BTN: 46 },
        { name: 'J85', CO: 16, BTN: 51 },
      ],
      'Dry Unpaired': [
        { name: 'AJ4', CO: 52, BTN: 40 },
        { name: 'Q75', CO: 10, BTN: 50 },
        { name: 'T72', CO: 23, BTN: 51 },
      ],
      'Straight': [
        { name: 'KQJds', CO: 23, BTN: 37 },
        { name: '987r', CO: 17, BTN: 43 },
        { name: '653ds', CO: 15, BTN: 47 },
      ],
      'Paired': [
        { name: 'A33r', CO: 60, BTN: 24 },
        { name: 'QQ5r', CO: 50, BTN: 58 },
        { name: '877ds', CO: 23, BTN: 39 },
      ],
      'Monotone': [
        { name: 'A92', CO: 38, BTN: 38 },
        { name: 'KJ8', CO: 16, BTN: 38 },
        { name: 'T54', CO: 31, BTN: 50 },
      ],
    },
  },
  '3bet Pot': {
    'BTNvBB': {
      'Dynamic Unpaired': [],
      'Dry Unpaired': [],
      'Straight': [],
      'Paired': [],
      'Monotone': [],
    },
    'COvBTN': {
      'Dynamic Unpaired': [],
      'Dry Unpaired': [],
      'Straight': [],
      'Paired': [],
      'Monotone': [],
    },
  },
};

const Tree = () => {
  const theme = useTheme();


  const [selectedPosition, setSelectedPosition] = useState(null);
  const [selectedTexture, setSelectedTexture] = useState(null);
  const [selectedPotType, setSelectedPotType] = useState('Single-Raised Pot');

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
    if (!selectedPosition || !selectedTexture) return [];
    return betFrequencies[selectedPotType][selectedPosition][selectedTexture];
  };

  const getBarConfig = () => {
    if (selectedPosition === 'BTNvBB') {
      return [
        { dataKey: 'BB', fill: theme.palette.primary.main },
        { dataKey: 'BTN', fill: theme.palette.secondary.main },
      ];
    } else {
      return [
        { dataKey: 'CO', fill: theme.palette.primary.main },
        { dataKey: 'BTN', fill: theme.palette.secondary.main },
      ];
    }
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
      </Paper>

      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
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
      </Paper>

      {selectedPosition && (
        <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
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
      )}

      {selectedPosition && selectedTexture && (
        <Card elevation={3}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Bet Sizes (% of Pot):
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(betSizes[selectedPotType][selectedPosition]).map(([player, sizes]) => (
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
                      {sizes[selectedTexture]}%
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

export default Tree;
