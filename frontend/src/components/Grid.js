import React, { useState } from 'react';
import { Grid, Card, Box, Typography, Tooltip } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    fold: { main: '#90caf9' },
    call: { main: '#66bb6a' },
    raise: { main: '#ff7043' },
  },
});

const hands = [
  ['AA', 'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s'],
  ['AKo', 'KK', 'KQs', 'KJs', 'KTs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s'],
  ['AQo', 'KQo', 'QQ', 'QJs', 'QTs', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s'],
  ['AJo', 'KJo', 'QJo', 'JJ', 'JTs', 'J9s', 'J8s', 'J7s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s'],
  ['ATo', 'KTo', 'QTo', 'JTo', 'TT', 'T9s', 'T8s', 'T7s', 'T6s', 'T5s', 'T4s', 'T3s', 'T2s'],
  ['A9o', 'K9o', 'Q9o', 'J9o', 'T9o', '99', '98s', '97s', '96s', '95s', '94s', '93s', '92s'],
  ['A8o', 'K8o', 'Q8o', 'J8o', 'T8o', '98o', '88', '87s', '86s', '85s', '84s', '83s', '82s'],
  ['A7o', 'K7o', 'Q7o', 'J7o', 'T7o', '97o', '87o', '77', '76s', '75s', '74s', '73s', '72s'],
  ['A6o', 'K6o', 'Q6o', 'J6o', 'T6o', '96o', '86o', '76o', '66', '65s', '64s', '63s', '62s'],
  ['A5o', 'K5o', 'Q5o', 'J5o', 'T5o', '95o', '85o', '75o', '65o', '55', '54s', '53s', '52s'],
  ['A4o', 'K4o', 'Q4o', 'J4o', 'T4o', '94o', '84o', '74o', '64o', '54o', '44', '43s', '42s'],
  ['A3o', 'K3o', 'Q3o', 'J3o', 'T3o', '93o', '83o', '73o', '63o', '53o', '43o', '33', '32s'],
  ['A2o', 'K2o', 'Q2o', 'J2o', 'T2o', '92o', '82o', '72o', '62o', '52o', '42o', '32o', '22']
];

const generateRandomStrategy = () => {
  const total = 100;
  const fold = Math.floor(Math.random() * total);
  const remainingTotal = total - fold;
  const call = Math.floor(Math.random() * remainingTotal);
  const raise = total - fold - call;
  return { fold, call, raise };
};

const PokerGrid = () => {
  const [strategy, setStrategy] = useState(
    hands.flat().reduce((acc, hand) => ({ ...acc, [hand]: generateRandomStrategy() }), {})
  );

  const getBackgroundGradient = (handStrategy) => {
    const { raise, call, fold } = handStrategy;
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
      <Typography variant="subtitle2">{hand}</Typography>
      <Typography variant="body2">Raise: {strategy[hand].raise}%</Typography>
      <Typography variant="body2">Call: {strategy[hand].call}%</Typography>
      <Typography variant="body2">Fold: {strategy[hand].fold}%</Typography>
    </Box>
  )

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ width: '100%', maxWidth: 1000, margin: 'auto', padding: 2 }}>
        <Typography variant="h4" gutterBottom>Strategy Grid</Typography>
        <Grid container spacing={0.5}>
          {hands.map((row, rowIndex) => (
            row.map((hand, colIndex) => (
              <Grid item xs={12/13} key={`${rowIndex}-${colIndex}`}>
                <Tooltip title={tooltipContent(hand)} arrow placement="top">
                  <Card 
                    sx={{ 
                      background: getBackgroundGradient(strategy[hand]),
                      height: 40,
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      cursor: 'pointer',
                      '&:hover': { opacity: 0.8 }
                    }}
                  >
                    <Typography variant="caption">{hand}</Typography>
                  </Card>
                </Tooltip>
              </Grid>
            ))
          ))}
        </Grid>
        <Box sx={{ marginTop: 2 }}>
          <Typography variant="subtitle1">Legend:</Typography>
          <Box display="flex" alignItems="center">
            <Box width={20} height={20} bgcolor={theme.palette.fold.main} mr={1} />
            <Typography variant="body2" mr={2}>Fold</Typography>
            <Box width={20} height={20} bgcolor={theme.palette.call.main} mr={1} />
            <Typography variant="body2" mr={2}>Call</Typography>
            <Box width={20} height={20} bgcolor={theme.palette.raise.main} mr={1} />
            <Typography variant="body2">Raise</Typography>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default PokerGrid;
