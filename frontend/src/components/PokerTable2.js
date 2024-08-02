import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent,
  IconButton
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CameraAltIcon from '@mui/icons-material/CameraAlt';

const TableContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  width: 800,
  height: 600,
  backgroundColor: theme.palette.success.main,
  borderRadius: '50%',
  // Remove overflow: 'hidden'
}));

const InnerTable = styled(Box)(({ theme }) => ({
  position: 'absolute',
  inset: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const CenterArea = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.success.dark,
  width: '75%',
  height: '50%',
  borderRadius: '50%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
}));

const PlayerSeat = styled(Box)(({ theme }) => ({
  position: 'absolute',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  // Add z-index to ensure player seats are above the table
  zIndex: 1,
}));

const PlayerName = styled(Typography)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  padding: theme.spacing(1),
  borderRadius: '50%',
  marginBottom: theme.spacing(0.5),
}));

const PlayerChips = styled(Typography)(({ theme }) => ({
  backgroundColor: theme.palette.grey[800],
  color: theme.palette.common.white,
  padding: theme.spacing(0.5),
  borderRadius: theme.shape.borderRadius,
}));

const ActionButton = styled(Button)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  '&:hover': {
    backgroundColor: theme.palette.primary.dark,
  },
}));

const PokerTable = () => {
  const [gameState, setGameState] = useState({
    players: [
      { name: 'Player 1', chips: 1500, hand: ['♠A', '♥K'] },
      { name: 'Player 2', chips: 1500, hand: ['♦Q', '♣J'] },
      { name: 'Player 3', chips: 1500, hand: ['♥10', '♠9'] },
      { name: 'Player 4', chips: 1500, hand: ['♣8', '♦7'] },
      { name: 'Player 5', chips: 1500, hand: ['♠6', '♥5'] },
      { name: 'Player 6', chips: 1500, hand: ['♦4', '♣3'] },
    ],
    communityCards: ['♠K', '♥Q', '♦J', '♣10', '♠9'],
    pot: 150,
    currentPlayer: 0,
  });

  const PlayerSeatComponent = ({ player, position }) => (
    <PlayerSeat sx={position}>
      <PlayerName variant="body2">{player.name}</PlayerName>
      <PlayerChips variant="body2">${player.chips}</PlayerChips>
    </PlayerSeat>
  );

  const CommunityCards = () => (
    <Box display="flex" justifyContent="center" gap={1} mb={2}>
      {gameState.communityCards.map((card, index) => (
        <Card key={index} sx={{ minWidth: 30, height: 45, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="body2">{card}</Typography>
        </Card>
      ))}
    </Box>
  );

  return (
    <Box position="relative" width={800} height={600}>
      <TableContainer>
        <InnerTable>
          <CenterArea>
            <CommunityCards />
            <Typography variant="h5" color="white" fontWeight="bold">Pot: ${gameState.pot}</Typography>
          </CenterArea>
        </InnerTable>
      </TableContainer>
      
      <PlayerSeatComponent player={gameState.players[0]} position={{ top: 0, left: '50%', transform: 'translateX(-50%)' }} />
      <PlayerSeatComponent player={gameState.players[1]} position={{ top: '25%', right: 20 }} />
      <PlayerSeatComponent player={gameState.players[2]} position={{ bottom: '25%', right: 20 }} />
      <PlayerSeatComponent player={gameState.players[3]} position={{ bottom: 0, left: '50%', transform: 'translateX(-50%)' }} />
      <PlayerSeatComponent player={gameState.players[4]} position={{ bottom: '25%', left: 20 }} />
      <PlayerSeatComponent player={gameState.players[5]} position={{ top: '25%', left: 20 }} />
      
      <Box position="absolute" bottom={16} left={16} display="flex" gap={1} zIndex={1}>
        <ActionButton variant="contained">Fold</ActionButton>
        <ActionButton variant="contained">Check</ActionButton>
        <ActionButton variant="contained">Bet</ActionButton>
      </Box>
      
      <IconButton 
        sx={{ position: 'absolute', top: 16, right: 16, color: 'white', zIndex: 1 }}
        aria-label="camera"
      >
        <CameraAltIcon />
      </IconButton>
    </Box>
  );
};

export default PokerTable;