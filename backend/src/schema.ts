import {
  intArg,
  makeSchema,
  nonNull,
  objectType,
  stringArg,
  inputObjectType,
  arg,
  asNexusMethod,
  enumType,
  booleanArg,
  idArg,
} from 'nexus'
import { DateResolver, DateTimeResolver } from 'graphql-scalars'
import { Context } from './context'

export const DateTime = asNexusMethod(DateResolver, 'date')

const Player = objectType({
  name: 'Player',
  definition(t) {
    t.id('id')
    t.string('name')
    t.string('mlbId')
    t.string('bbrefId')
    t.string('bbrefMinorsId')
    t.string('retroId')
    t.string('fangraphsId')
    t.string('fangraphsMinorMasterId')
    t.string('fullName')
    t.string('firstName')
    t.string('lastName')
    t.string('useName')
    t.string('middleName')
    t.string('matrilinealName')
    t.string('boxscoreName')
    t.int('primaryNumber')
    t.string('primaryPosition')
    t.date('birthDate')
    t.string('birthCity')
    t.string('birthStateProvince')
    t.string('birthCountry')
    t.int('height')
    t.int('weight')
    t.boolean('active')
    t.string('currentTeamId')
    t.string('parentOrgId'), t.int('fangraphsOrgProspectRanking')
    t.int('fangraphsOverallProspectRanking')
  },
})

const Query = objectType({
  name: 'Query',
  definition(t) {
    t.nonNull.list.field('allPlayers', {
      type: Player,
      resolve: (_parent, _args, context) => {
        return context.prisma.player.findMany()
      },
    })
    t.field('playerByMlbId', {
      type: Player,
      args: {
        mlbId: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findUnique({
          where: {
            mlbId: _args.mlbId,
          },
        }),
    })
    t.field('playerByBbrefId', {
      type: Player,
      args: {
        bbrefId: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findUnique({
          where: {
            bbrefId: _args.bbrefId,
          },
        }),
    })
    t.field('playerByRetroId', {
      type: Player,
      args: {
        retroId: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findUnique({
          where: {
            retroId: _args.retroId,
          },
        }),
    })
    t.field('playerById', {
      type: Player,
      args: {
        id: idArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findUnique({ where: { id: _args.id } }),
    })
    t.list.field('playersByFirstNameAndLastNameAndBirthDate', {
      type: Player,
      args: {
        firstName: stringArg(),
        lastName: stringArg(),
        birthDate: arg({ type: 'Date', description: 'YYYY-MM-DD' }),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            firstName: _args.firstName,
            lastName: _args.lastName,
            birthDate: _args.birthDate,
          },
        }),
    })
    t.list.field('playersByNameAndBirthDate', {
      type: Player,
      args: {
        name: stringArg(),
        birthDate: arg({ type: 'Date', description: 'YYYY-MM-DD' }),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            name: _args.name,
            birthDate: _args.birthDate,
          },
        }),
    })
    t.list.field('playersByName', {
      type: Player,
      args: {
        name: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            name: _args.name,
          },
        }),
    })
    t.list.field('playersByFirstNameAndLastName', {
      type: Player,
      args: {
        firstName: stringArg(),
        lastName: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            firstName: _args.firstName,
            lastName: _args.lastName,
          },
        }),
    })
    t.list.field('playersByFirstName', {
      type: Player,
      args: {
        firstName: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            firstName: _args.firstName,
          },
        }),
    })
    t.list.field('playersByLastName', {
      type: Player,
      args: {
        lastName: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            lastName: _args.lastName,
          },
        }),
    })
    t.list.field('allPlayersByParentOrgId', {
      type: Player,
      args: {
        parentOrgId: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            parentOrgId: _args.parentOrgId,
          },
        }),
    })
    t.list.field('allPlayersByBirthDate', {
      type: Player,
      args: {
        birthDate: arg({ type: 'Date', description: 'YYYY-MM-DD' }),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            birthDate: _args.birthDate,
          },
        }),
    })
    t.list.field('allPlayersByParentOrgId', {
      type: Player,
      args: {
        parentOrgId: stringArg(),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            parentOrgId: _args.parentOrgId,
          },
        }),
    })
    t.list.field('searchPlayers', {
      type: Player,
      args: {
        name: stringArg(),
        firstName: stringArg(),
        lastName: stringArg(),
        birthDate: arg({ type: 'Date', description: 'YYYY-MM-DD' }),
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.findMany({
          where: {
            OR: [
              { name: { contains: _args.name } },
              { firstName: { contains: _args.firstName } },
              { lastName: { contains: _args.lastName } },
              { birthDate: _args.birthDate },
            ],
          },
        }),
    }),
      t.list.field('allRankedProspectsByParentOrgId', {
        type: Player,
        args: {
          parentOrgId: stringArg(),
        },
        resolve: (_parent, _args, context) =>
          context.prisma.player.findMany({
            where: {
              parentOrgId: _args.parentOrgId,
              fangraphsOrgProspectRanking: { not: null },
            },
          }),
      })
  },
})

const playerArgs = {
  id: idArg(),
  name: stringArg(),
  mlbId: stringArg(),
  fullName: stringArg(),
  firstName: stringArg(),
  lastName: stringArg(),
  primaryNumber: intArg(),
  primaryPosition: stringArg(),
  birthDate: arg({ type: 'Date', description: 'YYYY-MM-DD' }),
  birthCity: stringArg(),
  birthCountry: stringArg(),
  birthStateProvince: stringArg(),
  height: intArg(),
  weight: intArg(),
  active: booleanArg(),
  useName: stringArg(),
  middleName: stringArg(),
  matrilinealName: stringArg(),
  retroId: stringArg(),
  fangraphsId: stringArg(),
  fangraphsMinorMasterId: stringArg(),
  bbrefId: stringArg(),
  bbrefMinorsId: stringArg(),
  currentTeamId: stringArg(),
  parentOrgId: stringArg(),
  fangraphsOrgProspectRanking: intArg(),
  fangraphsOverallProspectRanking: intArg(),
}

const mapArgsToPlayer = (args: any) => {
  return {
    id: args.id,
    name: args.name,
    mlbId: args.mlbId,
    retroId: args.retroId,
    fangraphsId: args.fangraphsId,
    fangraphsMinorMasterId: args.fangraphsMinorMasterId,
    bbrefId: args.bbrefId,
    bbrefMinorsId: args.bbrefMinorsId,
    firstName: args.firstName,
    middleName: args.middleName,
    lastName: args.lastName,
    primaryNumber: args.primaryNumber,
    primaryPosition: args.primaryPosition,
    birthDate: args.birthDate,
    birthCity: args.birthCity,
    birthCountry: args.birthCountry,
    birthStateProvince: args.birthStateProvince,
    height: args.height,
    weight: args.weight,
    active: args.active,
    useName: args.useName,
    currentTeamId: args.currentTeamId,
    parentOrgId: args.parentOrgId,
    fangraphsOrgProspectRanking: args.fangraphsOrgProspectRanking,
    fangraphsOverallProspectRanking: args.fangraphsOverallProspectRanking,
  }
}

const Mutation = objectType({
  name: 'Mutation',
  definition(t) {
    t.field('createPlayer', {
      type: Player,
      args: playerArgs,
      resolve: (_parent, _args, context) =>
        context.prisma.player.create({
          data: mapArgsToPlayer(_args),
        }),
    })
    t.field('updatePlayerById', {
      type: Player,
      args: {
        id: idArg(),
        ...playerArgs,
      },
      resolve: (_parent, _args, context) =>
        context.prisma.player.update({
          where: {
            id: _args.id,
          },
          data: mapArgsToPlayer(_args),
        }),
    })
    t.field('updatePlayerByMlbId', {
      type: 'Player',
      args: playerArgs,
      resolve: (_parent, _args, context) =>
        context.prisma.player.update({
          where: {
            mlbId: _args.mlbId,
          },
          data: mapArgsToPlayer(_args),
        }),
    })
    t.field('updatePlayerByRetroId', {
      type: 'Player',
      args: playerArgs,
      resolve: (_parent, _args, context) =>
        context.prisma.player.update({
          where: {
            retroId: _args.retroId,
          },
          data: mapArgsToPlayer(_args),
        }),
    })
    t.field('resetAllFangraphsRankings', {
      type: 'Player',
      resolve: (_parent, _args, context) =>
        context.prisma.player.updateMany({
          data: {
            fangraphsOrgProspectRanking: null,
            fangraphsOverallProspectRanking: null,
          },
        }),
    })
    //   t.field("updatePlayerByFangraphsId", {
    //     type: "Player",
    //     args: playerArgs,
    //     resolve: (_parent, _args, context) =>
    //       context.prisma.player.update({
    //         where: {
    //           fangraphsId: _args.fangraphsId,
    //         },
    //         data: mapArgsToPlayer(_args),
    //       }),
    //   });
    t.field('updatePlayerByBbrefId', {
      type: 'Player',
      args: playerArgs,
      resolve: (_parent, _args, context) =>
        context.prisma.player.update({
          where: {
            bbrefId: _args.bbrefId,
          },
          data: mapArgsToPlayer(_args),
        }),
    })
  },
})

export const schema = makeSchema({
  types: [Query, Mutation, DateTime, Player],
  outputs: {
    schema: __dirname + '/../schema.graphql',
    typegen: __dirname + '/generated/nexus.ts',
  },
  contextType: {
    module: require.resolve('./context'),
    export: 'Context',
  },
  sourceTypes: {
    modules: [
      {
        module: '@prisma/client',
        alias: 'prisma',
      },
    ],
  },
})
