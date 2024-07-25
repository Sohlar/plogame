import React, { useState } from 'react';
import { Grid, Card, Box, Typography, Tooltip, ToggleButton, ToggleButtonGroup, Paper } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#e0e0e0',
    },
    fold: { main: '#3370B3' },
    call: { main: '#4CAF50' },
    raise: { main: '#D55A3A' },
  },
});

const handCategories = {
  'Paired': ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22'],
  'A[K-T]': ['AK', 'AQ', 'AJ', 'AT'],
  'A[9-6]': ['A9', 'A8', 'A7', 'A6'],
  'A[5-2]': ['A5', 'A4', 'A3', 'A2'],
  '[K-T][K-T]': ['KQ', 'KJ', 'KT', 'QJ', 'QT', 'JT'],
  'Rundown': ['Rundown'],
  '1-gap': ['1-gap'],
  '2-gap': ['2-gap'],
  'Dangler': ['Dangler']
};

const suitDistributions = ['Double Suited', 'Single Suited', 'Rainbow'];

const generateRandomStrategy = () => {
  const total = 100;
  const fold = Math.floor(Math.random() * total);
  const remainingTotal = total - fold;
  const call = Math.floor(Math.random() * remainingTotal);
  const raise = total - fold - call;
  return { fold, call, raise };
};

const PLOStrategyGrid = () => {
  const [selectedDistribution, setSelectedDistribution] = useState('Double Suited');
  const [strategy, setStrategy] = useState(() => {
    const initialStrategy = {};
    Object.values(handCategories).flat().forEach(hand => {
      suitDistributions.forEach(suit => {
        initialStrategy[`${hand}-${suit}`] = generateRandomStrategy();
      });
    });
    return initialStrategy;
  });

  const handleDistributionChange = (event, newDistribution) => {
    if (newDistribution !== null) {
      setSelectedDistribution(newDistribution);
    }
  };

  const getBackgroundGradient = (handStrategy) => {
    const { fold, call, raise } = handStrategy;
    return `linear-gradient(to left, 
      ${theme.palette.fold.main} 0%, 
      ${theme.palette.fold.main} ${fold}%, 
      ${theme.palette.call.main} ${fold}%, 
      ${theme.palette.call.main} ${fold + call}%, 
      ${theme.palette.raise.main} ${fold + call}%, 
      ${theme.palette.raise.main} 100%)`;
  };

  const tooltipContent = (hand) => (
    <Box p={1}>
      <Typography variant="subtitle2">{hand} - {selectedDistribution}</Typography>
      <Typography variant="body2">Fold: {strategy[`${hand}-${selectedDistribution}`].fold}%</Typography>
      <Typography variant="body2">Call: {strategy[`${hand}-${selectedDistribution}`].call}%</Typography>
      <Typography variant="body2">Raise: {strategy[`${hand}-${selectedDistribution}`].raise}%</Typography>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ width: '100%', maxWidth: 1200, margin: 'auto', padding: 2, bgcolor: 'background.default' }}>
        <Typography variant="h4" gutterBottom color="text.primary">PLO Strategy Grid</Typography>
        <Box sx={{ mb: 2 }}>
          <ToggleButtonGroup
            value={selectedDistribution}
            exclusive
            onChange={handleDistributionChange}
            aria-label="suit distribution"
          >
            {suitDistributions.map((distribution) => (
              <ToggleButton key={distribution} value={distribution} aria-label={distribution}>
                {distribution}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>
        <Grid container spacing={2}>
          {Object.entries(handCategories).map(([category, hands], categoryIndex) => (
            <Grid item xs={12} sm={6} md={4} key={category}>
              <Paper 
                elevation={3} 
                sx={{ 
                  p: 2, 
                  bgcolor: 'background.paper', 
                  borderRadius: 2,
                  height: '100%'
                }}
              >
                <Typography variant="h6" gutterBottom color="text.primary">{category}</Typography>
                <Grid container spacing={1}>
                  {hands.map((hand) => (
                    <Grid item xs={4} sm={4} md={3} key={hand}>
                      <Tooltip title={tooltipContent(hand)} arrow placement="top">
                        <Card 
                          sx={{ 
                            background: getBackgroundGradient(strategy[`${hand}-${selectedDistribution}`]),
                            height: 40,
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            cursor: 'pointer',
                            '&:hover': { opacity: 0.8 }
                          }}
                        >
                          <Typography variant="caption" color="text.primary">{hand}</Typography>
                        </Card>
                      </Tooltip>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          ))}
        </Grid>
        <Box sx={{ marginTop: 2 }}>
          <Typography variant="subtitle1" color="text.primary">Legend:</Typography>
          <Box display="flex" alignItems="center">
            <Box width={20} height={20} bgcolor={theme.palette.fold.main} mr={1} />
            <Typography variant="body2" mr={2} color="text.primary">Fold</Typography>
            <Box width={20} height={20} bgcolor={theme.palette.call.main} mr={1} />
            <Typography variant="body2" mr={2} color="text.primary">Call</Typography>
            <Box width={20} height={20} bgcolor={theme.palette.raise.main} mr={1} />
            <Typography variant="body2" color="text.primary">Raise</Typography>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default PLOStrategyGrid;
