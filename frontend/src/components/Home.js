
import React, { useState, useEffect } from 'react';
import { Typography, Button, Container, Box, Grid, Paper, Avatar } from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import { Link } from 'react-router-dom';
import BarChartIcon from '@mui/icons-material/BarChart';
import SchoolIcon from '@mui/icons-material/School';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import { motion } from 'framer-motion';

const gradientAnimation = keyframes`
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
`;

const HeroSection = styled(Box)(({ theme }) => ({
  background: `linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab)`,
  backgroundSize: '400% 400%',
  animation: `${gradientAnimation} 15s ease infinite`,
  color: 'white',
  padding: theme.spacing(15, 0),
  textAlign: 'center',
  position: 'relative',
  overflow: 'hidden',
}));

const FloatingCard = styled(motion.div)(({ theme }) => ({
  background: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(3),
  boxShadow: theme.shadows[10],
  transition: 'all 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-10px)',
    boxShadow: theme.shadows[20],
  },
}));

const AnimatedNumber = ({ value, duration = 2000 }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = parseInt(value);
    if (start === end) return;

    let timer = setInterval(() => {
      start += 1;
      setCount(start);
      if (start === end) clearInterval(timer);
    }, duration / end);

    return () => clearInterval(timer);
  }, [value, duration]);

  return <span>{count.toLocaleString()}</span>;
};

function Home() {
  return (
    <Box>
      <HeroSection>
        <Container maxWidth="sm">
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
          >
            <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
              Welcome to PloGenius
            </Typography>
            <Typography variant="h5" paragraph>
              Master PLO Strategy with Advanced Tools and Analysis
            </Typography>
            <Button
              variant="contained"
              color="secondary"
              component={Link}
              to="/game"
              size="large"
              sx={{
                mt: 2,
                px: 4,
                py: 1.5,
                fontSize: '1.2rem',
                fontWeight: 'bold',
                borderRadius: '50px',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
                '&:hover': {
                  transform: 'translateY(-3px)',
                  boxShadow: '0 6px 25px rgba(0, 0, 0, 0.3)',
                },
              }}
            >
              Start Playing Now
            </Button>
          </motion.div>
        </Container>
      </HeroSection>

      <Container maxWidth="lg" sx={{ mt: -10, position: 'relative', zIndex: 1 }}>
        <Grid container spacing={4}>
          {[
            { icon: BarChartIcon, title: 'Advanced Analytics', description: 'Gain deep insights into your gameplay with our cutting-edge analysis tools.' },
            { icon: SchoolIcon, title: 'Comprehensive Training', description: 'Improve your skills with our tailored PLO training programs and exercises.' },
            { icon: EmojiEventsIcon, title: 'Competitive Edge', description: 'Stay ahead of the competition with our strategy recommendations and tips.' },
          ].map((item, index) => (
            <Grid item xs={12} md={4} key={index}>
              <FloatingCard
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.2 }}
              >
                <item.icon fontSize="large" color="primary" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h5" component="h3" gutterBottom fontWeight="bold">
                  {item.title}
                </Typography>
                <Typography>{item.description}</Typography>
              </FloatingCard>
            </Grid>
          ))}
        </Grid>
      </Container>

      <Box sx={{ my: 15, textAlign: 'center' }}>
        <Container maxWidth="md">
          <Typography variant="h3" component="h2" gutterBottom fontWeight="bold">
            PloGenius by the Numbers
          </Typography>
          <Grid container justifyContent="center" spacing={4}>
            {[
              { value: '10000', label: 'Active Users' },
              { value: '1000000', label: 'Hands Analyzed' },
              { value: '95', label: 'User Satisfaction' },
            ].map((stat, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Paper elevation={3} sx={{ p: 3, borderRadius: 4 }}>
                  <Typography variant="h3" color="primary" fontWeight="bold">
                    <AnimatedNumber value={stat.value} />
                    {stat.label === 'User Satisfaction' && '%'}
                  </Typography>
                  <Typography variant="subtitle1">{stat.label}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      <Box sx={{ my: 15, bgcolor: 'background.default', py: 10 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" gutterBottom fontWeight="bold" align="center">
            What Our Users Say
          </Typography>
          <Grid container spacing={4}>
            {[
              { name: 'John Doe', role: 'Professional Poker Player', comment: `PloGenius has completely transformed my PLO game. The insights I've gained are invaluable!` },
              { name: 'Jane Smith', role: 'Poker Enthusiast', comment: `The training exercises on PloGenius helped me identify and fix leaks in my strategy.` },
              { name: 'Mike Peterson', role: 'Poker Coach', comment: `I love how user-friendly and comprehensive PloGenius is. It's a must-have tool for any serious PLO player.` },
            ].map((testimonial, index) => (
              <Grid item xs={12} md={4} key={index}>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Paper elevation={3} sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <Typography variant="body1" paragraph>"{testimonial.comment}"</Typography>
                    <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                      <Avatar sx={{ width: 60, height: 60, mr: 2 }}>{testimonial.name.charAt(0)}</Avatar>
                      <Box>
                        <Typography variant="subtitle1" fontWeight="bold">{testimonial.name}</Typography>
                        <Typography variant="subtitle2" color="text.secondary">{testimonial.role}</Typography>
                      </Box>
                    </Box>
                  </Paper>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      <Box sx={{ my: 15, textAlign: 'center' }}>
        <Container maxWidth="sm">
          <Typography variant="h3" component="h2" gutterBottom fontWeight="bold">
            Ready to Elevate Your PLO Game?
          </Typography>
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to="/signup"
            size="large"
            sx={{
              mt: 4,
              px: 6,
              py: 2,
              fontSize: '1.4rem',
              fontWeight: 'bold',
              borderRadius: '50px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
              '&:hover': {
                transform: 'translateY(-3px)',
                boxShadow: '0 6px 25px rgba(0, 0, 0, 0.3)',
              },
            }}
          >
            Sign Up Now
          </Button>
        </Container>
      </Box>
    </Box>
  );
}

export default Home;

